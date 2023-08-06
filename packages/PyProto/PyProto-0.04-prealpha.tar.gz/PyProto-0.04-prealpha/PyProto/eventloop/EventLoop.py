from __future__ import unicode_literals

import heapq
import platform
import time
import socket
import os

from PyProto.eventloop.Events import (EVENT_IN, EVENT_OUT, EVENT_EXCEPT, 
                                      FDEvent, SocketEvent)
from PyProto.eventloop import Exceptions
from PyProto.utils import PriorityMap

# Import eventloops
try: from PyProto.eventloop.engines import epoll
except: from PyProto.eventloop.engines import nullengine as epoll
try: from PyProto.eventloop.engines import poll
except: from PyProto.eventloop.engines import nullengine as poll
try: from PyProto.eventloop.engines import _select as select
except: from PyProto.eventloop.engines import nullengine as select

class EventLoop:
    """Base eventloop class.

    This implements the eventloop of PyProto, selecting a given module for
    interfacing with the operating system's FD notification system.

    It also implements timers, e.g. events that fire at a given time.

    Errors in this class raise EventLoopException or another appropriate
    exception.
    """

    def __init__(self, evlooptype=None):
        """Initalise the eventloop.

        evlooptype should be a string with the FD notification system you want
        to use. Supported types are select (all platforms), epoll (Linux), and
        poll (windows, BSD, etc.)
        """
        self.evlooptype = evlooptype

        # Select best event loop
        if self.evlooptype == '' or self.evlooptype is None:
            self.evlooptype = self.best_evloop()

        if self.evlooptype == 'select':
            self.engine = select.SelectEventEngine()
        elif self.evlooptype == 'poll':
            self.engine = poll.PollEventEngine()
        elif self.evlooptype == 'epoll':
            self.engine = epoll.EpollEventEngine()
        else:
            raise EventLoopException("Unsupported eventloop type")

        # FD:Event map
        self.fdmap = dict()

        self.timermap = PriorityMap.PriorityMap()

        self.evloop_deadline = None

    @staticmethod
    def best_evloop():
        system = platform.system()
        if system == 'Linux':
            return 'epoll'
        # TODO: kqueue backend, but the kqueue python module sux
        elif system.endswith('BSD'):
            return 'poll'
        else:
            return 'select'

    def set_event(self, event, evtype, removemask=False):
        """Set an FDEvent/SocketEvent to be used for evtype. When the event
        happens the appropriate callback will be called in FDEvent/SocketEvent.

        Set removemask to remove the mask from the event.
        """
        if isinstance(event, FDEvent):
            readfd = event.readfd
            writefd = event.writefd
            if readfd == writefd:
                exceptfd = readfd
            else:
                exceptfd = None
        elif isinstance(event, SocketEvent):
            readfd = writefd = exceptfd = event.sock.fileno()
        else:
            raise ValueError("Unsupported event type")

        if evtype & EVENT_IN:
            if readfd is None:
                raise EventLoopException("Cannot set an event with EVENT_IN with no readfd!")
            self.set_fd(readfd, EVENT_IN, event, removemask)

        if evtype & EVENT_OUT:
            if writefd is None:
                raise EventLoopException("Cannot set an event with EVENT_OUT and no writefd!")
            self.set_fd(writefd, EVENT_OUT, event, removemask)

        if evtype & EVENT_EXCEPT:
            if exceptfd is None:
                raise EventLoopException("Ambiguous file descriptor for EVENT_EXCEPT, use EventLoop.set_fd instead")
            self.set_fd(exceptfd, EVENT_EXCEPT, event, removemask)

    # Remove an event by event object
    def remove_event(self, event):
        """Remove event by FDEvent."""
        if isinstance(event, FDEvent):
            self.remove_fd(event.readfd)
            self.remove_fd(event.writefd)
        elif isinstance(event, SocketEvent):
            self.remove_fd(event.sock.fileno())
        else:
            raise ValueError("Unsupported event type")

    # evtype should have read_callback, write_callback, and except_data events
    # depending on what you are listening for.
    def set_fd(self, fd, evtype, event=None, removemask=False):
        """Set event by fd, specifying the fdevent callback.
        
        If an fd has already been added to the event pool, event may be
        omitted. Otherwise event is mandatory. removemask specifies the
        given eventmask in evtype should be removed
        """
        if hasattr(fd, 'fileno'):
            fd = fd.fileno()

        if fd not in self.fdmap:
            if event is None:
                raise EventLoopException("Trying to add an empty event!")
            self.fdmap[fd] = [event, evtype]
            event.eventmask = evtype
            self.engine.register_fd(fd, self.fdmap[fd][1])
        else:
            if removemask:
                self.fdmap[fd][1] &= ~evtype
            else:
                self.fdmap[fd][1] |= evtype
            self.fdmap[fd][0].eventmask = self.fdmap[fd][1]
            self.engine.modify_fd(fd, self.fdmap[fd][1])

    def remove_fd(self, fd):
        """Remove an fd from the set"""
        if hasattr(fd, 'fileno'):
            fd = fd.fileno()

        if fd not in self.fdmap:
            return

        del self.fdmap[fd]
        self.engine.unregister_fd(fd)

    def set_timer(self, when, timerev, recur=False):
        """Create a timer to go off every when seconds
        
        timerev is the timer callback.
        Set recur to true for a recurring event, false for oneshot
        """
        timerev.last_ran = None
        timerev.recur = recur
        self.timermap.additem(when, timerev)

    def remove_timer(self, when=None, timerev=None, recur=None):
        """Remove a timer matching the given criteria"""
        for mwhen, mtimerev in list(self.timermap.items()):
            if when is not None and when != mwhen:
                continue

            if timerev is not None and timerev != mtimerev:
                continue

            if recur is not None and mtimerev.recur != recur:
                continue

            self.timermap.delitem(when, timerev)

    def process_timer(self):
        """Process each timer and return the time needed to sleep
        until the next event.

        Do not call this directly.
        """
        if len(self.timermap) == 0:
            return None

        # First compute when the next timer runs
        curtime = time.time() # Cached
        next_time = None
        runners = list()

        for when, timerlist in self.timermap.items():
            # Starting line (list is sorted -- so this will always be set
            # With the soonest timer)
            if next_time is None:
                next_time = when

            for timerev in timerlist:
                # Not run? pretend it was run now for timing purposes
                if timerev.last_ran is None:
                    timerev.last_ran = curtime

                # Calculate if it's eligible to be run yet
                # If not, the value we get will tell us how long to sleep
                # Disregard if curtime == last ran time, this means it was
                # just set or (unlikely) just run
                evinterval = curtime - timerev.last_ran
                if evinterval < when and evinterval > 0:
                    # See if sleep interval must be adjusted
                    if evinterval < next_time:
                        next_time = evinterval
                
                # Event eligible for running? Let's do this
                elif evinterval >= when:
                    runners.append((when, timerev))

        # If no events, return time to wait.
        if len(runners) == 0:
            return next_time

        # Run pending events
        time_taken = 0
        changed = False
        for when, timerev in runners:
            time_start = time.time()
            
            prev_len = self.timermap.len_all
            timer_result = timerev.run_timer() # Run the timer
            if self.timermap.len_all != prev_len:
                changed = True

            time_fin = time.time()
            timerev.last_ran = time_fin # Update the event.
            time_taken += time_fin - time_start
            
            # Remove this if we have to
            if not timerev.recur or timer_result == False:
                self.timermap.delitem(when, timerev)
                changed = True

            # Oh shit. We're too late.
            if time_taken >= next_time:
                return self.process_timer()

        # Check if our event list has been changed
        # If it hasn't, let's return, updating the time to the next event.
        # Otherwise, the wait time is possibly invalid -- recompute.
        if not changed:
            return next_time - time_taken

        # Recompute wait time 
        return self.process_timer()

    def run_once(self):
        """Run the eventloop once, firing timers also."""
        timeout = self.process_timer()
        starttime = time.time()
        # Run until we reach the timeout value...
        while True:
            events = self.engine.run_once(timeout)
            for fd, event in events:
                if event & EVENT_IN != 0:
                    if self.fdmap[fd][0].read_callback() == False:
                        self.set_fd(fd, EVENT_IN, removemask=True)
                if event & EVENT_OUT != 0:
                    if self.fdmap[fd][0].write_callback() == False:
                        self.set_fd(fd, EVENT_OUT, removemask=True)
                if event & EVENT_EXCEPT != 0:
                    if self.fdmap[fd][0].except_callback() == False:
                        self.set_fd(fd, EVENT_EXCEPT, removemask=True)

            if timeout is None:
                break

            curtime = time.time()
            if curtime - starttime >= timeout:
                break

            timeout -= (curtime - starttime)

    def run_forever(self):
        """Run the eventloop forever."""
        while True:
            self.run_once()

    def run_until(self, ticks):
        """Run for a given number of iterations"""
        for x in range(1, ticks):
            self.run_once()

