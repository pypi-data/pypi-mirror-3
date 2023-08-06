"""Wraps subprocess with pipe semantics and generator based multiplexing

pipe = open( somefile, 'rb' ) | nbio.Process( ['grep','blue'] ) | nbio.Process( ['wc','-l'])

"""
import os, select, fcntl, itertools, time, sys, popen2, signal, logging, subprocess, errno
log = logging.getLogger( __name__ )

class _DidNothing( object ):
    """Returned when a subprocess didn't do anything"""
    def __nonzero__( self ):
        return False
DID_NOTHING = _DidNothing()

class NBIOError( RuntimeError ):
    """Base class for nbio errors"""
class ProcessError( NBIOError ):
    """Called process returned an error code
    
    Attributes:
    
        process -- the Process (if applicable) which raised the error
    
    """
    process = None

def pause( duration ):
    """Allow tests to override sleeping using globalsub"""
    time.sleep( duration )

class Pipe( object ):
    """Pipe of N processes which all need to process data in parallel"""
    pause_on_silence = 0.01
    started = False
    def __init__( self, *processes ):
        self.processes = []
        if processes:
            first = self.append( self.get_component(processes[0]) )
            for process in processes[1:]:
                self.__or__( process )
    def __repr__( self ):
        return '%s => %s'%( 
            self.__class__.__name__, ' | '.join( [str(p) for p in self.processes]) 
        )
    def __getitem__(self, index):
        """Retrieve a particular item in the pipe"""
        return self.processes[index]
    def __len__( self ):
        """Return the number of items in this pipe"""
        return len( self.processes )
        
    def __iter__( self ):
        """Iterate over the processes in the pipe
        
        If the stdout/stderr of the processes is not captured, then we will 
        yield the results in whatever chunk-size is yielded from the individual 
        processes.
        
        If all of the processes yield DID_NOTHING in a particular cycle, then the 
        pipe will do a pause() for self.pause_on_silence (normally passed into the 
        __call__) before the next iteration.
        """
        try:
            self.started = True
            iterables = [ iter(process) for process in self.processes ]
            crashed = False
            while iterables and not crashed:
                exhausted = []
                something_happened = 0
                for iterable in iterables:
                    try:
                        child_result = iterable.next()
                        if child_result is DID_NOTHING:
                            pass
                        elif child_result:
                            something_happened += 1
                            yield child_result
                    except StopIteration, err:
                        exhausted.append( iterable )
                    except Exception, err:
                        # Have the *first* item that failed raise the error, 
                        # and only if they don't, raise this error...
                        for item in self.processes:
                            item.check_exit()
                        raise
                for done in exhausted:
                    while done in iterables:
                        iterables.remove( done )
                if not something_happened:
                    pause( self.pause_on_silence )
        finally:
            self.kill()
    def __call__( self, pause_on_silence=0.01 ):
        """Iterate over this pipeline, returning combined results as a string
        """
        result = []
        self.pause_on_silence = pause_on_silence
        for item in itertools.ifilter( bool, self ):
            if item:
                result.append( item )
        return "".join( result )
    def append( self, process ):
        """Add the given PipeComponent to this pipe (note: does not connect stdin/stdout)"""
        assert isinstance( process, PipeComponent ), process
        self.processes.append( process )
    def prepend( self, process ):
        """Add the given PipeComponent to this pipe (note: does not connect stdin/stdout)"""
        assert isinstance( process, PipeComponent ), process
        self.processes.insert( 0, process )
    @property
    def first( self ):
        """Retrieves the first item in the pipe"""
        if self.processes:
            return self.processes[0]
        raise IndexError( "No processes yet in this pipeline" )
    @property
    def last( self ):
        """Retrieves the last item in the pipe"""
        if self.processes:
            return self.processes[-1]
        raise IndexError( "No processes yet in this pipeline" )

    def __or__( self, other ):
        """Pipe our output into a process, callable or list"""
        other = self.get_component( other )
        log.debug( 
            'Hooking output of %s to input of %s', self.last, other 
        )
        self.last.iterables.append(
            other.iter_write( self.last.iter_read() )
        )
        self.append( other )
        return self
    def __ror__( self, other ):
        """Pipe output of other into our first item"""
        log.debug(
            'Hooking output of %s to input of %s', other, self.first 
        )
        other = self.get_component( other )
        self.first.iterables.append(
            self.first.iter_write( 
                other.iter_read()
            )
        )
        self.prepend( other )
        return self

    def __gt__( self, other ):
        """Pipe our output into a file
        """
        if isinstance( other, (str,unicode)):
            if other not in ('','-'):
                return self.__or__( open(other,'wb') )
            else:
                return self.__or__( other )
        else:
            return self.__or__( other )
    def __lt__( self, other ):
        """Pipe input from a named file"""
        if isinstance( other, (str,unicode)):
            if other not in ('','-'):
                return self.__ror__( open(other,'rb') )
            else:
                return self.__ror__( other )
        else:
            return self.__ror__( other )
    def get_component( self, other ):
        """Given a python object other, create a PipeComponent for it
        
        The purpose of this method is to allow for fairly "natural" 
        descriptions of tasks.  You can pipe to or from files, 
        to or from the string '-' (stdin/stdout), to the 
        string '' (collect stdout), or from a regular string (which is 
        treated as input).  You can pipe iterables into a pipe,
        you can pipe the result of pipes into callables.
        """
        if isinstance( other, PipeComponent ):
            pass 
        elif isinstance( other, file ):
            other = FileComponent( other )
        elif isinstance( other, (str,unicode)):
            if other == '-':
                other = FileComponent( sys.stdout, sys.stdin )
            elif other == '':
                other = IterComponent( )
            else:
                other = IterComponent( [other] )
        elif hasattr( other, '__iter__'):
            other = IterComponent( other )
        elif callable( other ):
            other = FunctionComponent( other )
        if not isinstance( other, PipeComponent ):
            raise TypeError( """Require a PipeComponent-compatible object, got: %s"""%(other,) )
        return other 
    def kill( self ):
        for process in self.processes:
            if hasattr( process, 'kill' ):
                try:
                    process.kill()
                except Exception, err:
                    log.warn(
                        "Unable to kill process: %s", process,
                    )
    

class PipeComponent( object ):
    live = True
    def __init__( self ):
        self.iterables = []
    def __iter__( self ):
        iterables = [ iter(x) for x in self.iterables ]
        while iterables and self.live:
            something_happened = 0
            exhausted = []
            for iterable in iterables:
                try:
                    child_result = iterable.next()
                    if child_result is DID_NOTHING:
                        pass
                    elif child_result:
                        something_happened += 1
                        yield child_result
                except StopIteration, err:
                    exhausted.append( iterable )
                except Exception, err:
                    err.args += (self,)
                    raise 
            for done in exhausted:
                while done in iterables:
                    iterables.remove( done )
            if not something_happened:
                yield DID_NOTHING
        self.check_exit()
    def check_exit( self ):
        pass
    def iter_read( self ):
        """Iterate reading from stdout"""
        raise TypeError( "Do not have an iter read for %s"%(self.__class__, ))
    def iter_write( self, source ):
        raise TypeError( "Do not have an iter write for %s"%(self.__class__, ))
    

class FileComponent( PipeComponent ):
    def __init__( self, filein,fileout=None ):
        self.stdin = filein
        self.stdout = fileout or filein 
        super( FileComponent, self ).__init__()
    def iter_read( self ):
        return reader( self.stdout )
    def iter_write( self, source ):
        return writeiter(
            source,
            self.stdin,
        )
    def __repr__( self ):
        if self.stdin != self.stdout:
            return '%s/%s'%( self.stdout, self.stdin )
        else:
            return 'file( %r, %r )'%( self.stdin.name, self.stdin.mode )
    
class Process( PipeComponent ):
    """A particular process in a Pipe
    
    Processes are the most common entry point when using nbio, you 
    create processes and pipe data into or out of them as appropriate
    to create Pipes.
    
    Under the covers the Process runs subprocess.Popen, and it accepts most of 
    the fields subprocess.Popen does.  By default it captures stdout and pipes 
    data into stdin.  If nothing is connected to stdin then stdin is closed on 
    the first iteration of the pipe.  If nothing is connected to stdout or 
    stderr (if stderr is captured) then the results will be returned to the 
    caller joined together with ''
    
    The implication is that if you do not want to store all of the results 
    in RAM, you need to "sink" the results into a process or file, or *not*
    capture the results (pass False for stdout or stderr).
    """
    stdin_needed = False
    stdout_needed = False 
    stderr_needed = False
    STDOUT = -1
    by_line = False
    def __init__( self, command, stderr=False, stdout=True, stdin = True,**named ):
        """Initialize the Process 
        
        command -- subprocess.Popen command string or list
                   if a string, and "shell" is not explicitly set, 
                   then will set "shell=True"
                   
        stdin -- whether to provide stdin writing 
        
        stdout -- whether to capture stdout 
        
        stderr -- whether to capture stderr, if -1, then combine stdout and stderr 
        
        good_exit -- if provided, iterable which provides the set of good exit codes 
                     which will not raise ProcessError when encountered
                     
        by_line -- if provided, will cause the output to be line-buffered so that 
                   only full lines will be reported, the '\\n' character will be used to 
                   split the output, so there will be no '\\n' character at the end of each 
                   line.
                   
        named -- passed to the subprocess.Popen() command 
        
        """
        if isinstance( command, (str,unicode)):
            if not 'shell' in named:
                named['shell'] = True 
        self.command = command 
        if 'good_exit' in named:
            self.good_exit = named.pop( 'good_exit' )
        else:
            self.good_exit = [0]
        if 'by_line' in named:
            self.by_line = named.pop( 'by_line' )
        self.pipe = self.start_pipe(stdin,stdout,stderr, **named)
        super( Process, self ).__init__( )
    def __unicode__( self ):
        return u'%s( %r )'%( self.__class__.__name__, self.command )
    __repr__ = __unicode__
    @property
    def stderr( self ):
        return self.pipe.stderr
    @property
    def stdout( self ):
        return self.pipe.stdout
    @property
    def stdin( self ):
        return self.pipe.stdin
    
    def start_pipe( self, stdin,stdout,stderr, **named ):
        """Start the captive process (internal operation)"""
        err = None
        if stderr == -1:
            stderr = subprocess.STDOUT
            stdout = True 
        else:
            stderr = [None,subprocess.PIPE][bool(stderr)]
        pipe = subprocess.Popen(
            self.command, 
            stdin = [None,subprocess.PIPE][bool(stdin)],
            stdout = [None,subprocess.PIPE][bool(stdout)],
            stderr = [None,subprocess.PIPE][bool(stderr)],
            **named
        )
        return pipe
    def __iter__( self ):
        """Iterate over the results of the process (normally done by the Pipe)"""
        if not self.stdout_needed:
            # nothing has been hooked to stdout
            if self.stdout:
                # but stdout was captured, so we need to consume it to prevent deadlocks
                self.iterables.append(
                    reader( self.stdout )
                )
        if not self.stderr_needed:
            # nothing has been hooked to stderr
            if self.stderr:
                self.iterables.append(
                    reader( self.stderr )
                )
        if not self.stdin_needed:
            # nothing is being sent in, so input is finished...
            close( self.stdin )
        return super( Process, self ).__iter__()
    
    def __or__( self, other ):
        """Pipe our output into a process, callable or list
        
        pipe = Pipe( Process( 'cat test.txt' ) | Process( 'grep blue' ) | [] )
        pipe()
        """
        self.stdout_needed = True 
        if isinstance( other, Pipe ):
            # Pipe our output into the pipe, add ourselves to the start of pipe...
            return other.__nor__( self )
        else:
            pipe = Pipe( self )
            return pipe.__or__( other )
        
    def __ror__( self, other ):
        """Pipe other into self"""
        self.stdin_needed = True 
        if isinstance( other, Pipe ):
            return other.__or__( self )
        else:
            pipe = Pipe( self )
            return pipe.__ror__( other )
    def __gt__( self, other ):
        """Pipe our output into a filename"""
        pipe = Pipe( self )
        return pipe.__gt__( other )
    def __lt__( self, other ):
        """Pipe our input from a filename"""
        pipe = Pipe( self )
        return pipe.__lt__( other )
    def __call__( self, *args, **named ):
        """Create a Pipe and run it with just this item as its children"""
        pipe = Pipe( self )
        return pipe( *args, **named )
    
    def check_exit( self ):
        """Check our exit code"""
        if self.pipe.returncode is None:
            exitcode = self.pipe.poll()
        else:
            exitcode = self.pipe.returncode
        if exitcode < 0:
            self.pipe.kill()
            exitcode = self.pipe.poll()
        if exitcode not in self.good_exit:
            err = ProcessError( 
                "Process %s returned error code %s"%( self.command, exitcode, ),
            )
            err.process = self 
            raise err

    def iter_read( self ):
        """Create the thing which iterates our read operation"""
        self.stdout_needed = True
        output = reader( self.stdout )
        if self.by_line:
            output = by_line( output )
        return output
    def iter_write( self, source ):
        """Create a thing which will read from source and write to us"""
        self.stdin_needed = True
        return writeiter(
            source,
            self.stdin,
        )
    def kill( self ):
        """Kill our underlying subprocess.Popen"""
        try:
            return self.pipe.kill( )
        except OSError, err:
            # we've already died/closed...
            pass 
    
class FunctionComponent( PipeComponent ):
    def __init__( self, function ):
        self.function = function 
        super( FunctionComponent, self ).__init__()
    def iter_read( self ):
        yield self.function()
    def iter_write( self, source ):
        return caller( source, self.function )
    def __str__( self ):
        return str( self.function )

class IterComponent( PipeComponent ):
    def __init__( self, iterable=None  ):
        self.iterable = iterable 
        super( IterComponent, self ).__init__()
    def iter_read( self ):
        return self.iterable
    def iter_write( self, other ):
        return other 
    def __repr__( self ):
        if self.iterable:
            return str( self.iterable )
        else:
            return '<str>'

def collector( iterable, target ):
    return caller( iterable, target.append )
def caller( iterable, target ):
    for item in iter(iterable):
        if item:
            target( item )
        yield item

def writeiter( iterator, fh ):
    """Write content from iterator to fh
    
    To write a file from a read file:
    
    .. code-block:: python
    
        writeiter(
            reader( open( filename )),
            fh 
        )
    
    To write a request.response object into a tar pipe iteratively:
    
    .. code-block:: python
    
        writeiter( 
            response.iter_content( 4096, decode_unicode=False ),
            pipe 
        )
    """
    total_written = 0
    assert hasattr( iterator, '__iter__'), iterator
    for content in iterator:
        if content and isinstance( content, (str,unicode)):
            for block_written in writer( content, fh ):
                total_written += block_written
                yield None
        else:
            yield DID_NOTHING
    close( fh )

def writer( content,fh, encoding='utf8' ):
    """Continue writing content (string) to fh until content is consumed
    
    Used by writeiter to writing individual bits of content to the fh
    """
    fp = fileno( fh )
    if isinstance( content, unicode ):
        content = content.encode( encoding )
    assert isinstance( content, str ), """Can only write string values: %r"""%(content)
    while content:
        try:
            written = os.write( fp, content )
        except ValueError, err:
            log.warn( 'Unconsumed content: %s', content )
            break
        if not written:
            yield DID_NOTHING
        else:
            content = content[written:]
            yield written
        
def reader( fh, blocksize = 4096 ):
    """Produce content blocks from fh without blocking
    """
    try:
        fd = fileno( fh )
    except ValueError, err:
        return 
    total = 0
    while not fh.closed:
        try:
            rr,rw,re = select.select([fh],[],[],0)
            if rr:
                result = os.read(fd, blocksize )
                if result == '':
                    break
            else:
                result = DID_NOTHING
        except ValueError, err:
            break 
        except (IOError,OSError), err:
            if err.args[0] in ( errno.EWOULDBLOCK,):
                if fh.closed:
                    break
                yield DID_NOTHING
            else:
                raise 
        else:
            yield result 
    close( fh )

def fileno( fh ):
    "Determine the fileno for the file-like thing"
    if hasattr( fh, 'fileno' ):
        return fh.fileno()
    return fh
def close( fh ):
    """Close the file/socket/closable thing"""
    if fh is sys.stdout or fh is sys.stderr:
        return
    if hasattr( fh, 'close'):
        errcode = fh.close()
    else:
        errcode = os.close( fileno(fh) )
    if errcode:
        raise RuntimeError( "Child process returned error code", errcode )
def by_line( iterable ):
    """Buffer iterable yielding individual lines"""
    buffer = ""
    for item in iterable:
        if not item:
            yield item 
        else:
            buffer += item 
            if '\n' not in item:
                # We did something, but we're not ready to yield a real value...
                yield None
            else:
                while '\n' in buffer:
                    line, buffer = buffer.split('\n',1)
                    yield line 
    if buffer:
        yield buffer 
