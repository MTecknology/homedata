#!/usr/bin/env python
'''
Provide a timeout decorator and exception

Usage:
    @timeout(<int>)
    def fun():
        pass

Author: Michael Lustfield
Copyright: Juniper Networks
License: GPLv3+
'''
import signal
import time


class TimedOutError(Exception):
    def __init__(self, value='Timed Out'):
        self.value = value

    def __str__(self):
        return repr(self.value)


def timeout(seconds):
    def decorate(f):

        def handler(signum, frame):
            raise TimedOutError()

        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            old_time_left = signal.alarm(seconds)
            # never lengthen existing timer
            if 0 < old_time_left < seconds:
                signal.alarm(old_time_left)
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
            finally:
                # deduct f's run time from the saved timer
                if old_time_left > 0:
                    old_time_left -= time.time() - start_time
                signal.signal(signal.SIGALRM, old)
                signal.alarm(old_time_left)
            return result
        new_f.__name__ = f.__name__
        return new_f

    return decorate
