# -*- coding: utf-8 -*-
"""
@author: todor.bukov
"""
from __future__ import print_function
import os
import sys
import glob
import shutil
import py2exe
from distutils.core import setup
from distutils.core import Command


SCRIPT_NAME = 'timerange'

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)

# ---
def remove_dir(dirname):
    if os.path.exists(dirname):
        shutil.rmtree(dirname)


# ---
def remove_file(afile):
    if os.path.exists(afile):
        os.remove(afile)


# ---
def find_files(path, file_pattern):
    result = []
    for root, dirs, files in os.walk(path):
        pattern = os.path.join(root,file_pattern)
        filelist = glob.glob(pattern)
        for f in filelist:
            if (not f in result) and (os.path.isfile(f)):
                result.append(f)
    return result


# ---
def read_txt_file(fname):
    """Read thw whole text file and returns it as a string"""
    result = ''
    with open(fname) as filevar:
        result = filevar.read()
    return result



# ---
class CleanCommand(Command):
    description = "cleans temporary files and build/dist directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd,'Must be in package root: %s' % self.cwd
        print("Script directory:", script_dir)
        
        print ("Removing ./build and ./dist directories")
        build_dir = os.path.join(os.getcwd(),'build')
        dist_dir = os.path.join(os.getcwd(),'dist')
        print ("  deleting ./buildir: ",build_dir)
        remove_dir(build_dir)        
        print ("  deleting ./dist: ",dist_dir)
        remove_dir(dist_dir)
        
        print ("Removing .pyc and .pyo compiled files")
        pyc_files = find_files(script_dir,"*.pyc")
        pyo_files = find_files(script_dir,"*.pyo")
        filelist = pyc_files + pyo_files
        for f in filelist:
            print ('  deleting:',f)
            os.remove(f)
            
        print("Removing .exe files")
        exe_files = find_files(script_dir,"*.exe")
        for f in exe_files:
            print ('  deleting:',f)
            os.remove(f)
            
        print("Cleaning complete.")

# ---
# Not necessary, use "python setup.py py2exe" command line instead
#sys.argv.append('py2exe')

# ensure the script in the local dir is loaded
local_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.insert(0, local_path)
import timerange

VERSION = timerange.VERSION
AUTHOR = timerange.AUTHOR
AUTHOR_EMAIL = timerange.AUTHOR_EMAIL
LICENSE = timerange.LICENSE

LONG_DESCRIPTION = read_txt_file('README.txt')


setup(
    name = SCRIPT_NAME,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = 'Generates list of dates in various formats',
    version = VERSION,
    long_description = LONG_DESCRIPTION,
    license = LICENSE,
    url = 'https://bitbucket.org/todor/timerange',
    classifiers = 
        [
        # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        # Licensed under GPL v.3 or later
        'License :: OSI Approved :: GNU General Public License (GPL)', 
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        ],
    options = {'py2exe':{
                            'bundle_files': 1
                        }
              },
    console = [SCRIPT_NAME + ".py"],
    zipfile = None,
    scripts = [SCRIPT_NAME + ".py"],
    platforms=['any'],
    cmdclass={
        'clean': CleanCommand
    },
  
)
