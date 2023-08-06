#! /usr/bin/env python
"""Install a given firmware package onto the file system (commands fussy-install and fussy-clean)

Major TODO items:

* TODO: error handling for all of the big issues (disk-space, memory, script failures)
"""
import subprocess, os, sys, shutil, tempfile, glob
from optparse import OptionParser
from fussy import unpack, errors

CURRENT_LINK = 'current'
FAILSAFE_NAME = 'failsafe'
PROTECTED = [CURRENT_LINK,FAILSAFE_NAME]
DEFAULT_FIRMWARE_DIRECTORY = '/opt/firmware'

def clean( target=DEFAULT_FIRMWARE_DIRECTORY, protected = None ):
    """Naive cleaning implementation
    
    Removes all names in target which are not in protected,
    paths in protected must be *full* path names, as returned 
    by glob.  The target of the current link is protected.
    """
    if protected is None:
        protected = [
            os.path.join( target, p ) 
            for p in PROTECTED
        ]
    # current target is always protected...
    current = os.path.join( target, CURRENT_LINK)
    assert os.path.exists( current ), "Current link appears to be missing, corrupt installation  (e.g. run install)?"
    current_target = final_path( current )
    assert os.path.exists( current_target ), "Current link appears to be broken, fix before cleaning (e.g. run install)"
    protected.append( current_target )
    for path in glob.glob( os.path.join( target, '*' )):
        if path not in protected:
            shutil.rmtree( path, True )

def final_path( link ):
    """Get the final path of the given link"""
    return os.path.normpath( os.path.realpath( link ) )

def swap_link( final_target, current ):
    """Swap current link to point to final_target
    
    Steps taken:
    
        * if there is an existing tmp link, remove it 
        * create a tmp link to the final target 
        * rename tmp link to `current`
    
    returns None
    """
    tmp = current + '~'
    try:
        os.remove( tmp )
        # TODO: address race condition, you should have the while upgrade 
        # cron-locked, but that's not obvious here...
    except (OSError,IOError), err:
        pass
    os.symlink( final_target, tmp )
    os.rename( tmp, current )

def install_bytes( filename, keyring='/etc/fussy/keys', target='/opt/firmware' ):
    """Install the packaged bytes into a final target directory
    
    Steps taken:
    
        * unpack firmware using :func:`fussy.unpack.unpack`
        * rsync new_firmware into /opt/firmware (`target`)
            * if `CURRENT_LINK` (current) is present in `target`, 
              will hard-link shared files between the new firmware and `current` 
              to reduce disk use (using :command:`rsync` parameter --link-dest)
        * removes the temporary directory where unpacking was performed
    
    returns full path to sub-directory of target where new firmware was installed
    
    raises Errors on most failures, including disk-full, failed commands, missing 
    executables, etc
    """
    temp_dir = unpack.unpack( filename, keyring )
    assert os.path.exists( temp_dir )
    base_name = os.path.basename( temp_dir )
    try:
        final_target = os.path.join( os.path.normpath( target ), base_name )
        i=0
        while os.path.exists( final_target ):
            i+= 1
            final_target = os.path.join( os.path.normpath( target ), base_name + '-%i'%(i,) )
        current = os.path.join( os.path.normpath( target ), 'current' )
        command = [
            'rsync', '-aq',
        ]
        if os.path.exists( current ):
            command.append( '--link-dest=%s'%( current,),)
        # TODO: figure out some way to configure rsync to not create a second 
        # level directory when told `rsync -a a b`
        command.extend([
            os.path.join( temp_dir, x )
            for x in os.listdir( temp_dir )
        ])
        command.extend([
            final_target,
        ])
        subprocess.check_call( command )
        return final_target
    finally:
        shutil.rmtree( temp_dir, True )

def enable( final_target, current ):
    """Attempt to enable final_target as the current release
    
    Steps taken:
    
        * runs `final_target/.pre-install final_target` 
          (iff .pre-install is present)
        * (atomically) swaps the link `current` 
          for a link that points to `final_target`
        * runs `final_target/.post-install final_target` 
          (iff .post-install is present)
        * if a failure occurs before swap-link completes,
          deletes final_target 
    
    returns None 
    raises Exceptions on lots of failure cases
    """
    pre_install = os.path.join( final_target, '.pre-install' )
    post_install = os.path.join( final_target, '.post-install' )
    
    try:
        if os.path.exists( pre_install ):
            subprocess.check_call( [
                pre_install,
                final_target,
            ])
        swap_link( final_target, current )
    except Exception, err:
        # we failed in either pre-setup or swapping
        shutil.rmtree( final_target, True )
        raise
    
    if os.path.exists( post_install ):
        subprocess.check_call([
            post_install,
            final_target,
        ])

def install( filename, keyring='/etc/fussy/keys', target='/opt/firmware' ):
    """Install given firmware <filename> into given target directory
    
    Steps taken:

        * unpack firmware (using :func:`fussy.install.install_bytes`)
        * enable firmware (using :func:`fussy.install.enable`)
        * if :func:enable fails, enable `previous` 
          (or `failsafe` if there was no previous)
    
    returns (error_code (0 is success), path name of the installed package)
    """
    current = os.path.join( os.path.normpath( target ), CURRENT_LINK )
    failsafe = os.path.join( os.path.normpath( target ), FAILSAFE_NAME )
    
    previous = None
    if os.path.exists( current ):
        previous = final_path( current )
        if not os.path.exists( previous ):
            previous = None
    if not previous and os.path.exists( failsafe ) :
        previous = failsafe
    
    final_target = install_bytes( filename, keyring, target )
    assert os.path.exists( final_target )
    try:
        enable( final_target, current )
    except Exception, err:
        if previous:
            enable( previous, current )
            raise errors.RevertedFailure( previous )
        raise errors.UnrecoverableError( str(err) )
        # TODO: need lots more logic in the back-off code...
    else:
        return final_target

def get_options():
    """Creates the OptionParser used in :func:`main` """
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
        default = unpack.DEFAULT_KEYRING,
        action="store",
        type="string",
        help="GPG keyring to use for verification/decryption (default /etc/fussy/keys)",
    )
    parser.add_option(
        '-t','--target',
        dest = 'target',
        default = DEFAULT_FIRMWARE_DIRECTORY,
        action="store",
        type="string",
        help="Directory into which to rsync the firmware (default /opt/firmware)",
    )
    return parser

def main():
    """Main entry-point for the fussy-install script
    
    Steps taken:
    
        * parses arguments 
        * launches :func:`install`
    """
    parser = get_options()
    options,args = parser.parse_args()
    if not options.file:
        if args:
            options.file = args[0]
        else:
            parser.error( "Need a file to install" )
    return install( options.file, options.keyring, options.target )

def clean_main():
    """Main entry-point for fussy-clean script 
    
    Steps taken:
    
        * parses arguments 
        * launches :func:`clean`
    """
    parser = OptionParser()
    parser.add_option(
        '-t','--target',
        dest = 'target',
        default = DEFAULT_FIRMWARE_DIRECTORY,
        action="store",
        type="string",
        help="Directory into which to rsync the firmware (default /opt/firmware)",
    )
    options,args = parser.parse_args()
    error_code, installed = clean( options.target )
    # TODO: return codes to say "backed off", not just success/failure
    return error_code
