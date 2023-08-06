#!/usr/bin/env python

from distutils.core import setup
from cwrap import __version__ as cwv
import sys , os , shutil

MANPATHS = (
    '/usr/man' ,
    '/usr/share/man' ,
    '/usr/local/man' ,
    '/usr/local/share/man'
)

def installMan(manpage):
    # Check for the man location
    for d in MANPATHS:
        man1 = os.path.join(d , 'man1')
        if os.path.isdir(d) and os.path.isdir(man1):
            # We have found a man directory, install!
            dest = os.path.normpath(os.path.join(man1 , manpage))
            print 'Copying %s to %s' % (manpage , dest)
            shutil.copyfile(manpage , dest)
            os.system('gzip -9 %s' % dest)

setup(name='cron-wrap' ,
    version=cwv ,
    author='Jay Deiman' ,
    author_email='admin@splitstreams.com' ,
    url='http://stuffivelearned.org/doku.php?id=programming:python:cwrap' ,
    description='A cron job wrapper used to suppress output' ,
    long_description='Full documentation can be found in the man page or here: '
        'http://stuffivelearned.org/doku.php?id=programming:python:cwrap' ,
    scripts=['cwrap.py']
)



if 'install' in sys.argv:
    # Try to install the man page
    installMan('./cwrap.py.1')
