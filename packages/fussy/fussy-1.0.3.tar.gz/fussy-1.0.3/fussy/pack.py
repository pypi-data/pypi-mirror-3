#! /usr/bin/env python
"""Bundle a package as a signed firmware for installation/redistribution
"""
import tempfile, subprocess, os, sys, datetime, glob
from optparse import OptionParser

DEFAULT_EXCLUDES = [
    '.svn',
    '.bzr',
    '.git',
]

def pack( root_dir, excludes=None, encrypt_for=None ):
    """Bundle directory into a firmware file...
    
    * root_dir -- directory to be packed into the firmware, the 
        :func:`os.path.basename` of this directory will be the name used 
        in the created bundle filename and the directory installed into 
        the target on client machines
    * excludes -- patterns to exclude from the firmware image (passed to
        :command:`tar` during packing)
    * encrypt_for -- if specified also encrypts for the given key, should 
        be the key ID, fingerprint, or (unique) email
    
    returns absolute filename for generated gpg firmware 
    (created in a temporary directory)
    """
    temp_dir = tempfile.mkdtemp(prefix='fussy-',suffix='-pack')
    firmware_name = os.path.basename( root_dir )
    if firmware_name == 'current':
        raise RuntimeError( 'Cannot create a firmware named "current"')
    tar_name = firmware_name+ '.tar.gz'
    tar_file = os.path.join( temp_dir, tar_name )
    gpg_file = tar_file + '.gpg'
    command = [
        'tar','-zcf',
        tar_file,
    ] + [
        '--exclude=%s'%(x,) 
        for x in ((excludes or []) + DEFAULT_EXCLUDES)
    ] + [os.path.basename(root_dir)]
    subprocess.check_call( command, cwd=os.path.dirname( os.path.abspath(root_dir) ) )
    if encrypt_for:
        subprocess.check_call( [ 'gpg', '-se', '-r', encrypt_for, tar_file] )
    else:
        subprocess.check_call( [ 'gpg', '--sign', tar_file] )
    assert os.path.exists( gpg_file )
    os.remove( tar_file )
    return gpg_file

def get_options():
    """Produces the OptionParser for :func:main"""
    parser = OptionParser()
    parser.add_option( 
        '-x','--exclude', 
        dest='exclude', 
        action="append",
        type="string",
        help="Paths/patterns to exclude from the archive",
    )
    parser.add_option(
        '-r','--root',
        dest = 'root',
        default='firmware',
        type="string",
        help="The directory to be packed for distribution, should be a versioned/unique name, for instance including a human-readable timestamp",
    )
    parser.add_option(
        '-e','--encrypt-for',
        dest = 'encrypt',
        action="store",
        type="string",
        help="The name of the key for which to encrypt (otherwise just sign)",
    )
    return parser
    
def main():
    """Main function for the packing script"""
    options,args = get_options().parse_args()
    gpg_file = pack( options.root, options.exclude, options.encrypt )
    print gpg_file 
    return 0
