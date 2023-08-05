# $Id: setup.py 6 2007-05-28 20:41:53Z horcicka $

from distutils.core import setup

long_description = '''
Lock files are used on Unix-like systems as a means of synchronization
among processes. Only one process can hold a lock file. Other processes
that want to acquire it have to wait until it is released by the
holder.

In this module the lock file is implemented as an empty regular file,
exclusively locked using fcntl.flock. The file is removed when it is to
be released.
'''

setup(
    name='lock_file',
    version='1.0',
    description = 'Lock file manipulation',
    long_description = long_description,
    author = 'Martin Horcicka',
    author_email = 'martin@horcicka.eu',
    url = 'http://martin.horcicka.eu/python/lock_file/',
    download_url
    = 'http://martin.horcicka.eu/python/lock_file/lock_file-1.0.tar.gz',
    py_modules = ['lock_file'],
    license = 'Public Domain',
    platforms = 'Unix-like systems',
    classifiers = [
    'License :: Public Domain',
    'Operating System :: POSIX'])
