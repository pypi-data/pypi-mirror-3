#!/usr/bin/env python

#fix a bug that setuptools creates:
import distutils.filelist
findall = distutils.filelist.findall  

import sys
import os
#print sys.argv

py_version = sys.version
use_setuptools = False

if sys.argv == ['setup.py', 'sdist']:
    print 'using regular setup tools'
    from distutils.core import setup
else:
    try:    
        from setuptools import setup
        distutils.filelist.findall = findall #reset
        use_setuptools = True
    except ImportError:
        print 'using regular setup tools'
        from distutils.core import setup

#bring in release_version 
basedir = os.path.split(__file__)[0]
if basedir:
    basedir += '/'
for line in open(basedir + 'src/versioninfo.py').readlines():
    if (line.startswith('release_version')):
        exec(line.strip())
        
def abort(msg):    
    sys.stderr.write(msg + '\n')
    sys.exit(1)
    

if py_version < '2.5':
    abort('Python must be > 2.5 to use picloud')
elif py_version > '3':
    abort('This package cannot be used under python3.  Please get the python3 package from http://www.picloud.com')


#for setup tools, we need dependecies on simplejson for python2.5
#NOTE: We also want the user to have multiprocessing and openssl; 
# unfortunately, they will not build on all systems 
if py_version < '2.6':
    requires = ["simplejson"]
else:
    requires = []

#source install deps checking
if not use_setuptools:
    try:
        import json
    except ImportError:
        try:
            import simplejson
        except ImportError:        
            abort('simplejson must be installed to use picloud\nDownload it at http://pypi.python.org/pypi/simplejson/2.0.9/')

#check for pywin32 on windows:
#This can't be installed from pypi automatically, so just crash here
if os.name == 'nt':
    try: 
        import win32con
    except ImportError:
        abort('Python for Windows extensions must be installed to use picloud.\nDownload them at http://sourceforge.net/projects/pywin32/')
        
setup(name='cloud',
      version=release_version,  #defined by versioninfo.py exec
      description='PiCloud client-side library',      
      author='PiCloud, Inc.',
      author_email='contact@picloud.com',
      url='http://www.picloud.com',
      install_requires = requires,
      license='GNU LGPL',
      long_description=open('README.txt').read(),
      packages=['cloud', 'cloud.serialization', 'cloud.transport', 'cloud.util', 'cloud.util.cloghandler'],
      package_dir = {'cloud': basedir+'src'},
      #package_data= {'' : ['README, PKG-INFO, LICENSE']}, #cloghandler included in picloud
      package_data= {'cloud.util.cloghandler' : ['README, PKG-INFO, LICENSE']}, #cloghandler included in picloud
      platforms=['CPython 2.5', 'CPython 2.6', 'CPython 2.7'],      
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Networking',
        
        ]
     )


import os

import sys

if 'install' in sys.argv:    
    try:  #Config writing can fail if there are permissions problems
        import cloud.util.writeconfig as writeconfig
        writeconfig.doReload = True
        writeconfig.writeConfig()
        
        #hack for SUDO users
        sudouid = os.environ.get('SUDO_UID')
        if sudouid:
            import cloud.cloudconfig as cc
            confname = cc.fullconfigpath+cc.configname
            os.chown(confname, int(sudouid),  int(os.environ.get('SUDO_GID')))
            os.chown(cc.fullconfigpath, int(sudouid),  int(os.environ.get('SUDO_GID')))
    except:
        pass


#WARNININGS ON MISSING OPTIONAL DEPENDENCIES
try:
    import multiprocessing
except ImportError:
    sys.stderr.write('multiprocessing module must be installed to use the PiCloud simulator and cloud.mp.\nDownload it at http://pypi.python.org/pypi/multiprocessing/')        


try:
    import ssl
except ImportError:
    try:
        import OpenSSL
    except ImportError:
        sys.stderr.write('OpenSSL python bindings not installed.  These are highly recommended to ensure a secure connection to Picloud.\nDownload them at http://pypi.python.org/pypi/pyOpenSSL/0.9')
