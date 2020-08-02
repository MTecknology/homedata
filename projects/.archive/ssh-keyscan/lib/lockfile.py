#!/usr/bin/env python
'''
Provides a self-expiring lock file handler.

Usage:
    lock = LockFile('/run/sshscan.pid').acquire()
    if not lock:
        print('Lock already held; not executing')
        sys.exit(1)

Author: Michael Lustfield
Copyright: Juniper Networks
License: GPLv3+
'''
import os
import socket


class LockFile(object):
    '''Class to handle creating and removing (pid) lockfiles'''

    # custom exceptions
    class FileLockAcquisitionError(Exception):
        pass

    class FileLockReleaseError(Exception):
        pass

    def __init__(self, path):
        self.pid = os.getpid()
        self.host = socket.gethostname()
        self.path = path

    def acquire(self):
        '''Acquire a lock, returning self if successful, False otherwise'''
        if self.islocked():
            return False
        try:
            fh = open(self.path, 'w')
            fh.write(self.addr())
            fh.close()
        except BaseException:
            if os.path.isfile(self.path):
                try:
                    os.unlink(self.path)
                except BaseException:
                    pass
                raise self.FileLockAcquisitionError(
                        'Error acquiring lock: %s' % self.fddr())
        return self

    def release(self):
        '''Release lock, returning self'''
        if self.ownlock():
            try:
                os.unlink(self.path)
            except BaseException:
                raise self.FileLockReleaseError(
                       'Error releasing lock: %s' % self.fddr())
        return self

    def _readlock(self):
        '''Internal method to read lock info'''
        try:
            lock = {}
            fh = open(self.path)
            data = fh.read().rstrip().split('@')
            fh.close()
            lock['pid'], lock['host'] = data
            return lock
        except BaseException:
            return {'pid': 8**10, 'host': ''}

    def islocked(self):
        '''Check if we already have a lock'''
        try:
            lock = self._readlock()
            os.kill(int(lock['pid']), 0)
            return (lock['host'] == self.host)
        except BaseException:
            return False

    def ownlock(self):
        '''Check if we own the lock'''
        lock = self._readlock()
        return (self.fddr() == self.pddr(lock))

    def __del__(self):
        '''Magic method to clean up lock when program exits'''
        self.release()

    # convenience callables for formatting
    def addr(self):
        '''Print a formatted address, "<pid>@<host>"'''
        return '{}@{}'.format(self.pid, self.host)

    def fddr(self):
        '''Print a formatted address, "<path>@<addr>"'''
        return '<{} {}>'.format(self.path, self.addr())

    def pddr(self, lock):
        '''Print a formatted address, "<path> <pid>@@<host>"'''
        return '<{} {}@{}>'.format(self.path, lock['pid'], lock['host'])
