"""
Note this module will only work with Python 2.x, in the processing of porting to function
in both Python 2.x and Python 3.x
This is the md5_sum_glob function. The purpose of this function is to
MD5 Checksum a glob of files at a $PATH example: /opt/C_FILES/ibm.*
"""

import hashlib, glob

def md5_checksum(file_name):
    use_md5_hash = hashlib.md5()
    use_md5_hash.update(open(file_name).read())
    return use_md5_hash.hexdigest() + '\t' + file_name

def glob_files(path_name):
    glob_paths = glob.glob(path_name)
    for path in glob_paths:
        print(md5_checksum(path))
        
"""
Example:

#!/usr/bin/python

import glob
from globchecksum import glob_files

path_name = '/opt/archive/IBM*'
glob_paths = glob.glob(path_name)
glob_files(path_name)

"""