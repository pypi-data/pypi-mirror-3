"""Link all files in a distribution from relative location on the hard disk"""
import os, logging
from optparse import OptionParser

log = logging.getLogger( __name__ )

def link_tree( distribution_dir, target_dir='/', symbolic=True ):
    """(Sym)link all files under distribution_dir from target_dir 
    """
    if symbolic:
        link = os.symlink 
    else:
        link = os.link
    for path, subdirs, filenames in os.walk( distribution_dir ):
        dir_relative = os.path.relpath( path, distribution_dir )
        dir_source = os.path.normpath( os.path.abspath( path ) )
        dir_final = os.path.normpath( os.path.join( target_dir, dir_relative ))
        if not os.path.exists( dir_final ):
            log.info( 'Creating directory: %s', dir_final )
            try:
                os.makedirs( dir_final )
            except Exception, err:
                err.args += (dir_final,)
                raise 
        for filename in filenames:
            file_source = os.path.join( dir_source, filename )
            file_final = os.path.join( dir_final, filename )
            if os.path.lexists( file_final ):
                if (
                    symbolic and 
                    os.path.islink( file_final ) and 
                    os.readlink( file_final ) == file_source
                ):
                    log.info( 'Up to date: %s', file_final )
                    continue
                try:
                    log.info( 'Replacing: %s', file_final )
                    temp = file_final + '~'
                    if os.path.exists( temp ):
                        try:
                            os.remove( temp )
                        except Exception, err:
                            err.args += (temp, )
                            raise 
                    link( file_source, temp )
                    os.rename( temp, file_final )
                except Exception, err:
                    log.error( "Error linking %s: %s", file_final, err )
                    raise err
            else:
                log.info( 'Linking: %s', file_final )
                link( file_source, file_final )
    
def get_options():
    """Creates the OptionParser used in :func:`main` """
    parser = OptionParser()
    parser.add_option(
        '-d','--directory',
        dest = 'directory',
        default = None,
        help="Directory to which to link",
    )
    parser.add_option(
        '-t','--target',
        dest = 'target',
        default = None,
        help="Directory in which to create the links",
    )
    return parser

def main():
    logging.basicConfig( level=logging.INFO )
    options,args = get_options().parse_args()
    if args:
        if not options.directory:
            options.directory = args[0]
            args = args[1:]
        if args and not options.target:
            options.target = args[0]
            args = args[1:]
    link_tree( options.directory, options.target )
    return 0
