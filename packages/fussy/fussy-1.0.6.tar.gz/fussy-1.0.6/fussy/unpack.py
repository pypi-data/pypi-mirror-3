"""Unpack a signed .tar.gz.asc or .tar.gz.gpg archive into a temporary directory
"""
import subprocess, tempfile, os, sys, shutil, glob, logging, traceback
from optparse import OptionParser
from fussy import errors, nbio
log = logging.getLogger( __name__ )

DEFAULT_KEYRING = '/etc/fussy/keys'

def verify_requirements( directory, requirements ):
    """Verify that the directory has the expected files
    
    requirements -- list of files expected to exist in the directory,
        should be minimal, we've already crypto-verified the source, 
        this is just to prevent signed-but-defective installations
    
    raises 
    """
    for requirement in requirements:
        if not os.path.exists( os.path.join( directory, requirement )):
            raise RuntimeError( "Missing path: %r"%( requirement, ))

def unpack( filename, keyring=DEFAULT_KEYRING ):
    """Unpack (uploaded) filename into temporary directory
    """
    source = os.path.abspath( os.path.normpath( filename ) )
    directory = tempfile.mkdtemp( prefix='fussy-', suffix='-unpacked' )
    def report_progress( line ):
        log.info( 'unpack: %s', line )
    try:
        env = os.environ.copy()
        env['GNUPGHOME'] = keyring
        try:
            pipe = (
                nbio.Process( ['gpg', '-d', source], env=env ) | 
                    nbio.Process( ['tar','-zx'], cwd=directory ) |
                        report_progress 
            )
            try:
                pipe()
            except Exception, err:
                pipe.kill()
                raise
        except nbio.ProcessError, err:
            log.error( "Traceback: %s", traceback.format_exc())
            if err.process.command[0] == 'gpg':
                log.error( 'gpg reported failure' )
                raise errors.SignatureFailure( 
                    "Unable to verify signature"
                )
            else:
                log.error( 'tar reported failure' )
                raise errors.ArchiveFailure(
                    "Unable to unpack the archive: %s"%( str(err))
                )
        except Exception, err:
            log.error( "Unhandled error Traceback: %s", traceback.format_exc())
            raise 
        # there should now be *precisely* one firmware directory and 
        # potentially 2 upgrade scripts (which don't match *)
        files = glob.glob( os.path.join( directory, '*' ))
        if len(files) != 1:
            raise errors.ArchiveFailure( "Expected a single root directory, got: %s"%(files,))
        directory = files[0]
        if os.path.basename( directory ) in ['current']:
            raise errors.ArchiveFailure( "Do not allow creation of archives with name current" )
    except Exception, err:
        shutil.rmtree( directory, True )
        raise
    return directory

def get_options():
    parser = OptionParser()
    parser.add_option(
        '-f','--file',
        dest = 'file',
        default = None,
        action="store",
        type="string",
        help="The firmware archive to unpack, must be a .tar.gz.gpg or a .tar.gz.asc",
    )
    parser.add_option(
        '-k','--keyring',
        dest = 'keyring',
        default = '/etc/fussy/keys',
        action="store",
        type="string",
        help="GPG keyring to use for verification/decryption (default /etc/fussy/keys)",
    )
    return parser
    
def main():
    parser = get_options()
    options,args = parser.parse_args()
    if not options.file:
        if args:
            options.file = args[0]
        else:
            parser.error( "Need a file to unpack" )
    directory = unpack( options.file or args[0], keyring=options.keyring )
    print directory
    return 0
