"""
A heapq-based scheduler for asyncore.

License: MIT
"""

import sys
import time
import heapq
import asyncore
import traceback
import errno

_tasks = []

class CallLater(object):
    """Calls a function at a later time.

    It can be used to asynchronously schedule a call within the polling
    loop without blocking it. The instance returned is an object that
    can be used to cancel or reschedule the call.
    """

    def __init__(self, seconds, target, *args, **kwargs):
        """
         - (int) seconds: the number of seconds to wait
         - (obj) target: the callable object to call later
         - args: the arguments to call it with
         - kwargs: the keyword arguments to call it with; a special
           '_errback' parameter can be passed: it is a callable
           called in case target function raises an exception.
        """
        assert callable(target), "%s is not callable" % target
        assert sys.maxint >= seconds >= 0, "%s is not greater than or equal " \
                                           "to 0 seconds" % seconds
        self._delay = seconds
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._errback = kwargs.pop('_errback', None)
        self._repush = False
        # seconds from the epoch at which to call the function
        self.timeout = time.time() + self._delay
        self.cancelled = False
        heapq.heappush(_tasks, self)

    def __le__(self, other):
        return self.timeout <= other.timeout

    def call(self):
        """Call this scheduled function."""
        assert not self.cancelled, "Already cancelled"
        try:
            try:
                self._target(*self._args, **self._kwargs)
            except (KeyboardInterrupt, SystemExit, asyncore.ExitNow):
                raise
            except:
                if self._errback is not None:
                    self._errback()
                else:
                    raise
        finally:
            if not self.cancelled:
                self.cancel()

    def reset(self):
        """Reschedule this call resetting the current countdown."""
        assert not self.cancelled, "Already cancelled"
        self.timeout = time.time() + self._delay
        self._repush = True

    def delay(self, seconds):
        """Reschedule this call for a later time."""
        assert not self.cancelled, "Already cancelled."
        assert sys.maxint >= seconds >= 0, "%s is not greater than or equal " \
                                           "to 0 seconds" % seconds
        self._delay = seconds
        newtime = time.time() + self._delay
        if newtime > self.timeout:
            self.timeout = newtime
            self._repush = True
        else:
            # XXX - slow, can be improved
            self.timeout = newtime
            heapq.heapify(_tasks)

    def cancel(self):
        """Unschedule this call."""
        assert not self.cancelled, "Already cancelled"
        self.cancelled = True
        del self._target, self._args, self._kwargs, self._errback
        if self in _tasks:
            pos = _tasks.index(self)
            if pos == 0:
                heapq.heappop(_tasks)
            elif pos == len(_tasks) - 1:
                _tasks.pop(pos)
            else:
                _tasks[pos] = _tasks.pop()
                heapq._siftup(_tasks, pos)


class CallEvery(CallLater):
    """Calls a function every x seconds.
    It accepts the same arguments as CallLater and shares the same API.
    """

    def call(self):
        # call this scheduled function and reschedule it right after
        assert not self.cancelled, "Already cancelled"
        exc = False
        try:
            try:
                self._target(*self._args, **self._kwargs)
            except (KeyboardInterrupt, SystemExit, asyncore.ExitNow):
                exc = True
                raise
            except:
                if self._errback is not None:
                    self._errback()
                else:
                    exc = True
                    raise
        finally:
            if not self.cancelled:
                if exc:
                    self.cancel()
                else:
                    self.timeout = time.time() + self._delay
                    heapq.heappush(_tasks, self)


def _scheduler():
    """Run the scheduled functions due to expire soonest (if any)."""
    now = time.time()
    while _tasks and now >= _tasks[0].timeout:
        call = heapq.heappop(_tasks)
        if call._repush:
            heapq.heappush(_tasks, call)
            call._repush = False
            continue
        try:
            call.call()
        except (KeyboardInterrupt, SystemExit, asyncore.ExitNow):
            raise
        except:
            print traceback.format_exc()

def close_all(socket_map=None, ignore_all=False):
    """Close all scheduled functions and opened sockets."""
    if socket_map is None:
        socket_map = asyncore.socket_map
    for x in socket_map.values():
        try:
            x.close()
        except OSError, x:
            if x[0] == errno.EBADF:
                pass
            elif not ignore_all:
                raise
        except (asyncore.ExitNow, KeyboardInterrupt, SystemExit):
            raise
        except:
            if not ignore_all:
                asyncore.socket_map.clear()
                del _tasks[:]
                raise
    socket_map.clear()

    for x in _tasks:
        try:
            if not x.cancelled:
                x.cancel()
        except (asyncore.ExitNow, KeyboardInterrupt, SystemExit):
            raise
        except:
            if not ignore_all:
                del _tasks[:]
                raise
    del _tasks[:]


def loop(timeout=30, use_poll=False, socket_map=None, count=None):
    """Start asyncore and scheduler loop.
    Use this as replacement of the original asyncore.loop() function.
    """
    if use_poll and hasattr(asyncore.select, 'poll'):
        poll_fun = asyncore.poll2
    else:
        poll_fun = asyncore.poll
    if socket_map is None:
        socket_map = asyncore.socket_map
    if count is None:
        while (socket_map or _tasks):
            _scheduler()
            if _tasks:
                poll_fun(_tasks[0].timeout, socket_map)
            else:
                poll_fun(timeout, socket_map)            
    else:
        while (socket_map or _tasks) and count > 0:
            _scheduler()
            if _tasks:
                poll_fun(_tasks[0].timeout, socket_map)
            else:
                poll_fun(timeout, socket_map)
            count -= 1
