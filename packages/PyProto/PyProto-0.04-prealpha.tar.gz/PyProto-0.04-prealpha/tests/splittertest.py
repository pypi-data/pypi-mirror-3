#!/usr/bin/env python3

from __future__ import unicode_literals, print_function

from sys import path, stderr
import os
import socket
from PyProto.eventloop import EventLoop, Events
from PyProto.splitter import LineSplitter
from PyProto.utils import Printer

try:
    import gc
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_STATS)
except Exception as e:
    print("No garbage collection information will be spewed, error:", str(e))
    gc = None

class IRCProtocol(LineSplitter.LineSplitter):
    @Printer.print_lines
    def read_line(self, line):
        rawline = line
        # Blow away
        if line[1] == ':':
            line = line[1:]
            hostname = True

        lastparam = None
        if line.find(':') != -1:
            line, sep, lastparam = line.partition(':')

        params = line.split(' ')
        if lastparam:
            params.append(lastparam)

        if hostname:
            host = params[0]
            del params[0]
        else:
            host = None

        if params[0] == 'PING':
            self.write_line('PONG :{}'.format(params[1]))

        return rawline

event = EventLoop.EventLoop()
splitter = LineSplitter.LineSplitter(event, host="irc.staticbox.net", port=6667, ipv6=False)
splitter.connect()
splitter.write_line("USER shitbot * 8 :I suck")
splitter.write_line("NICK shitbot")
event.run_forever()

