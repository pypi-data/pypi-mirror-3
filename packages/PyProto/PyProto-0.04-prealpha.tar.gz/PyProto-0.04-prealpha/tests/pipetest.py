#!/usr/bin/env python3

from __future__ import unicode_literals, print_function

from sys import path, stderr
from PyProto.eventloop import EventLoop, Events
from os import write, read, pipe
from string import ascii_letters, digits, punctuation
from random import choice, randint

try:
    import gc
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_STATS)
except Exception as e:
    print("No garbage collection information will be spewed, error:", str(e))
    gc = None

# Here is a basic test of the event system using a pipe

class PipeEvent(Events.FDEvent):
    def read_callback(self):
        f = read(self.readfd, 50)
        print("Recieved data from fd = {}:".format(self.readfd), f.decode('UTF-8'))
        return True

    def write_callback(self):
        x = ''.join([choice(ascii_letters + digits + punctuation + ' ') for x in range(randint(5, 50))])
        print("Writing bytes to fd = {}:".format(self.writefd), x)
        write(self.writefd, x.encode('UTF-8'))
        return False

class TimerEvent(Events.TimerEvent):
    def __init__(self, event, writefd, evid):
        super(TimerEvent, self).__init__(event)
        self.writefd = writefd
        self.evid = evid
        
    def run_timer(self):
        print("Timer event #{} fired!".format(self.evid))
        self.event.set_fd(writefd, Events.EVENT_OUT)

class QuitEvent(Events.TimerEvent):
    def run_timer(self):
        print("Quitting time!")
       
        global gc
        if gc:
            print("Garbage unfreed: {}".format(gc.garbage))

        quit()

# Test it selects a default...
event = EventLoop.EventLoop()

# create our pipe pair
readfd, writefd = pipe()

fdevent = PipeEvent(event, (readfd, writefd))
timerevent = TimerEvent(event, writefd, 1)
timerevent2 = TimerEvent(event, writefd, 2)
quitevent = QuitEvent(event)

event.set_timer(5, timerevent, recur=True)
event.set_timer(3, timerevent2, recur=True)
event.set_timer(60, quitevent, recur=False)
event.set_event(fdevent, Events.EVENT_IN|Events.EVENT_OUT)
event.run_forever()
