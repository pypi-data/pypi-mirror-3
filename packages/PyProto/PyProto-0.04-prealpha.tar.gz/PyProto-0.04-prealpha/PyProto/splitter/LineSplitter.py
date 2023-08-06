from __future__ import unicode_literals

import os
from collections import deque

from PyProto.eventloop import EventLoop, Events
from PyProto.splitter import Exceptions
from PyProto.utils import Printer, Errors 

# Line util.for line-ending delimited protocols
class LineSplitter(Events.SocketEvent):
    def __init__(self, event, line_end='\r\n', read_count=512, encoding='UTF-8', **kwargs):
        super(LineSplitter, self).__init__(event, **kwargs)

        self.line_end = line_end
        self.line_buf = deque()
        self.read_count = read_count
        self.encoding = encoding

    def read_callback(self):
        super(LineSplitter, self).read_callback()
        lines = self.read_buffer.decode(self.encoding).split(self.line_end)
        self.read_buffer = lines[-1].encode(self.encoding)

        for line in lines[:-1]:
            self.read_line(line)

        return True

    def write_callback(self):
        while True:
            try:
                self.write_buffer += self.line_buf.popleft()
            except IndexError:
                return False # Drained

            res = super(LineSplitter, self).write_callback()

            if res:
                # Put back on line buffer.
                self.line_buf.append(self.write_buffer)
                return True

    @Printer.print_lines
    def read_line(self, line):
        return line

    @Printer.print_lines
    def write_line(self, line, raw=False):
        if not raw and (line.rfind(self.line_end) == -1):
            line += self.line_end

        self.line_buf.append(line.encode(self.encoding))
        self.event.set_event(self, EventLoop.EVENT_OUT)
        return line

