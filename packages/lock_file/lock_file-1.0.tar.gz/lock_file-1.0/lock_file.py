# $Id: lock_file.py 7 2007-05-28 20:42:41Z horcicka $

'''Lock file manipulation.

Lock files are used on Unix-like systems as a means of synchronization
among processes. Only one process can hold a lock file. Other processes
that want to acquire it have to wait until it is released by the
holder.

In this module the lock file is implemented as an empty regular file,
exclusively locked using fcntl.flock. The file is removed when it is to
be released.

Example: Ensuring that only one instance of a script is running

    import sys
    from lock_file import LockFile, LockError

    try:
        lock_f = LockFile('/var/run/app.lock')
    except LockError:
        sys.exit('An instance of this script is already running')

    try:
        do_something_useful()
    finally:
        lock_f.release()

Example: Waiting until the lock file can be acquired

    from lock_file import LockFile

    lock_f = LockFile('/var/run/app.lock', wait = True)
    try:
        do_something_useful()
    finally:
        lock_f.release()

Example: Waiting until the lock file can be acquired (in Python 2.5 and
higher)

    from __future__ import with_statement

    from lock_file import LockFile

    with LockFile('/var/run/app.lock', wait = True):
        do_something_useful()
'''

__all__ = 'LockError', 'LockFile'

import fcntl
import os


class LockError(Exception):
    '''Lock error.

    This exception is raised if a lock file cannot be acquired at that
    moment and waiting for the acquisition is not allowed.
    '''

    def __init__(self, message):
        Exception.__init__(self, message)


    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self.args[0]) + ')'


class LockFile(object):
    '''Lock file.

    This class represents an acquired lock file. After its releasing
    most methods lose their sense and raise a ValueError.
    '''

    def __init__(self, path, wait = False):
        '''Initialize and acquire the lock file.

        Creates and locks the specified file. The wait argument can be
        set to True to wait until the lock file can be acquired.

        Raises:
            OSError	- if any OS operation fails
            LockError	- if the lock file cannot be acquired at that
			  moment and the wait argument is False
        '''

        object.__init__(self)
        self._path = path
        self._fd = None

        # Acquire the lock file
        while self._fd is None:
            # Create the file
            fd = os.open(path, os.O_CREAT | os.O_WRONLY)
            try:
                # Acquire a lock
                if wait:
                    fcntl.flock(fd, fcntl.LOCK_EX)
                else:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except IOError:
                        raise LockError('File is locked: ' + repr(self._path))

                try:
                    # Check if the locked file is the required one (it could
                    # have been removed and possibly recreated between the
                    # opening and the lock acquisition)
                    try:
                        stat1 = os.stat(path)
                    except OSError:
                        pass
                    else:
                        stat2 = os.fstat(fd)
                        if stat1.st_dev == stat2.st_dev \
                            and stat1.st_ino == stat2.st_ino:

                            self._fd = fd

                finally:
                    # Unlock the file if it is not the required one
                    if self._fd is None:
                        fcntl.flock(fd, fcntl.LOCK_UN)

            finally:
                # Close the file if it is not the required one
                if self._fd is None:
                    os.close(fd)


    def __enter__(self):
        if self._fd is None:
            raise ValueError('The lock file is released')

        return self


    def __repr__(self):
        repr_str = '<'
        if self._fd is None:
            repr_str += 'released'
        else:
            repr_str += 'acquired'

        repr_str += ' lock file ' + repr(self._path) + '>'
        return repr_str


    def get_path(self):
        if self._fd is None:
            raise ValueError('The lock file is released')

        return self._path


    def fileno(self):
        if self._fd is None:
            raise ValueError('The lock file is released')

        return self._fd


    def release(self):
        '''Release the lock file.

        Removes, unlocks and closes the lock file.

        Raises:
            ValueError	- if the lock file is already released
            OSError	- if any OS operation fails
        '''

        if self._fd is None:
            raise ValueError('The lock file is released')

        # Remove, unlock and close the file
        try:
            os.remove(self._path)
        finally:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            finally:
                try:
                    os.close(self._fd)
                finally:
                    self._fd = None


    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
