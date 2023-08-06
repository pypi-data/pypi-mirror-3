"""
Helper class for a lock with a timeout

Use as follows:

with botnee.timeout_lock.TimeOutLock(botnee_config._timout):
    # do stuff

"""

import threading
import time

from botnee import debug

class TimeoutLock(object):
    def __init__(self, lock, timeout):
        self._lock = threading.Lock()
        #self._lock = lock
        self._cond = threading.Condition(threading.Lock())
        self._timeout = timeout

    def __enter__(self):
        if self.wait(self._timeout):
            return self
        else:
            return None

    def wait(self, timeout, verbose=True):
        self._cond.acquire()
        current_time = start_time = time.time()
        print "Requesting lock"
        while current_time < start_time + timeout:
            if self._lock.acquire(False):
                debug.print_verbose("Acquired lock", verbose)
                return True
            else:
                debug.print_verbose("Waiting for lock", verbose)
                self._cond.wait(timeout - current_time + start_time)
                current_time = time.time()
        return False

    def __exit__(self, type, value, traceback, verbose=True):
        try:
            self._lock.release()
        except Exception:
            pass
        
        self._cond.notify()
        #self._cond.release()
        debug.print_verbose("Released lock", verbose)
        #self._lock.release()
