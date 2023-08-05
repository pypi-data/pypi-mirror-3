#!/usr/bin/env python

import os
import sys

#fix a bug that setuptools creates:
import distutils.filelist
findall = distutils.filelist.findall  

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

# bring in release_version
basedir = os.path.split(__file__)[0]

for line in open(os.path.join(basedir, 'src/versioninfo.py')).readlines():
    if (line.startswith('release_version')):
        exec(line.strip())
        
def abort(msg):    
    sys.stderr.write(msg + '\n')
    sys.exit(1)


if sys.version < '2.5':
    abort('Python must be > 2.5 to use PiCloud')
elif sys.version > '3':
    abort('This package cannot be used under Python3. Please get the Python3 package from http://www.picloud.com')


#Python2.5 lacks important packages like ssl and (simple)json. Discover if needed
requires = []

#source install deps checking
try:
    import json
except ImportError:
    try:
        import simplejson
    except ImportError:
        if not use_setuptools:        
            abort('simplejson must be installed to use picloud\nDownload it at http://pypi.python.org/pypi/simplejson/')
        else:
            requires.append("simplejson")
            
try:
    import ssl
except ImportError:
    try:
        import OpenSSL
    except ImportError:
        if not use_setuptools:
            abort('OpenSSL python bindings not installed.  These are required to ensure a secure connection to Picloud.\nDownload them at http://pypi.python.org/pypi/ssl')
        else: #inject requirement
            requires.append('ssl')

#check for pywin32 on windows which is highly recommended:
#These can't be isntalled automatically, so just warn
if os.name == 'nt':
    try: 
        import win32con
    except ImportError:
        sys.stderr.write('Python for Windows extensions are highly recommended for using picloud.\nDownload them at http://sourceforge.net/projects/pywin32/')

setup(name='cloud',
      version=release_version,  #defined by versioninfo.py exec
      description='PiCloud client-side library',      
      author='PiCloud, Inc.',
      author_email='contact@picloud.com',
      url='http://www.picloud.com',
      install_requires=requires,
      license='GNU LGPL',
      long_description=open('README.txt').read(),
      packages=['cloud', 'cloud.cli', 'cloud.serialization', 'cloud.transport', 'cloud.util', 'cloud.util.cloghandler'],
      package_dir = {'cloud': os.path.join(basedir, 'src')},
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
        
        ],
      #data_files=[('/etc/bash_completion.d', ['bash_completion.d/picloud'])],
      entry_points={
          'console_scripts': [
              'picloud = cloud.cli.main:main',]
        },
     )

if 'install' in sys.argv:
    print ''
    print '********************************************************'
    print '********************************************************'
    print '***                                                  ***'
    print '***  Please run "picloud setup" to complete install  ***'
    print '***                                                  ***'
    print '********************************************************'
    print '********************************************************'
    print ''
