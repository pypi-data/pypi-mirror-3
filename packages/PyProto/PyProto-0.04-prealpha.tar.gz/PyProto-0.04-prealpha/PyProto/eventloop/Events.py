from collections import Sequence
import errno
import socket
import abc

from PyProto.eventloop import Exceptions
from PyProto.utils import Errors

EVENT_IN = 1
EVENT_OUT = 2
EVENT_EXCEPT = 4

class BaseEvent(object):
    """ Base for all event objects """

    __slots__ = ('event')

    def __init__(self, event):
        """ Initalise the BaseEvent """
        if event is None:
            raise ValueError("Invalid event type")
        self.event = event

class BaseDescriptorEvent(BaseEvent):
    """Events that can happen on any sort of descriptor"""

    __slots__ = ('read_buffer', 'write_buffer')

    def __init__(self, event, readlen=512):
        self.readlen = readlen
        self.read_buffer = self.write_buffer = b''
        super(BaseDescriptorEvent, self).__init__(event)

    def read_callback(self):
        """This is called when a read event fires in the eventloop.

        Override this in child classes to alter behaviour.
        """
        read_list = list()
        try:
            while True:
                read_list.append(self.do_read(self.readlen))
        except (IOError, OSError) as e:
            if not Errors.ignore_errno(e.errno):
                raise
        finally:
            self.read_buffer += b''.join(read_list)

        return True

    def write_callback(self):
        """This is called when a write event fires in the eventloop.

        Override this in child classes to alter behaviour.
        """
        if self.write_buffer is None:
            return False # wat.

        if hasattr(self.write_buffer, 'encode'):
            buf = self.write_buffer.encode('UTF-8')
        else:
            buf = self.write_buffer

        writelen = len(self.write_buffer)
        try:
            while writelen > 0:
                written = self.do_write(self.write_buffer)
                self.write_buffer = self.write_buffer[written:]
                writelen -= written
        except (IOError, OSError) as e:
            if not Errors.ignore_errno(e.errno):
                raise
            if writelen > 0:
                return True

        return False

    def except_callback(self):
        """This does nothing yet."""
        pass

    @abc.abstractmethod
    def do_read(self, length):
        pass

    @abc.abstractmethod
    def do_write(self, buf):
        pass

class FDEvent(BaseDescriptorEvent):
    def __init__(self, event, fd):
        """Initalise the FDEvent

        fd should be a sequence pair of the format
        readfd = [0], writefd = [1], or a file number.
        If it is not a pair, read and write
        fd will be congruent.

        set event to your EventLoop for internal uses.
        """

        super(FDEvent, self).__init__(event)

        if isinstance(fd, Sequence):
            self.readfd, self.writefd = fd[0], fd[1]
        elif hasattr(fd, 'fileno'):
            self.readfd = self.writefd = fd.fileno()
        else:
            self.readfd = self.writefd = fd

        if self.readfd:
            self.event.set_event(self, EVENT_IN)
        if self.writefd:
            self.event.set_event(self, EVENT_OUT)

    def do_read(self, length):
        return os.read(self.readfd, length)

    def do_write(self, buf):
        return os.write(self.writefd, buf)


class SocketEvent(BaseDescriptorEvent):
    """Like FDEvent, but for sockets"""

    __slots__ = ('ipv6', 'host', 'port', 'sock', 'bindhost', 'bindport')

    def __init__(self, event, **kwargs):
        super(SocketEvent, self).__init__(event)

        self.ipv6 = kwargs.get('ipv6', True)
        self.host = kwargs.get('host', None)
        self.port = kwargs.get('port', None)
        self.sock = kwargs.get('socket', None)
        self.bindhost = kwargs.get('bindhost', None)
        self.bindport = kwargs.get('bindport', None)
        proto = kwargs.get('proto', socket.SOCK_STREAM)

        if self.ipv6:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET

        if self.sock is None:
            self.sock = socket.socket(family, proto)
            self.sock.setblocking(False)
        elif isinstance(sock, socket.socket):
            self.sock = sock
        else:
            raise ValueError("socket attribute must be an actual socket")       

        self.event.set_event(self, EVENT_IN)
        self.event.set_event(self, EVENT_OUT)
  
    def connect(self, hostport=tuple(), bindhostport=tuple()):
        if len(hostport) >= 2:
            host = hostport[0]
            port = hostport[1]
        else:
            host = self.host
            port = self.port

        if len(bindhostport) >= 2:
            bindhost = bindhostport[0]
            bindport = bindhostport[1]
        else:
            bindhost = self.bindhost
            bindport = self.bindport
        
        if bindhost is not None and bindport is not None:    
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((bindhost, bindport))

        try:
            self.sock.connect((host, port))
        except (IOError, OSError) as e:
            if not Errors.ignore_errno(e.errno):
                raise

        # When we're connected, this will fire. =)
        self.event.set_event(self, EVENT_OUT)

        return True

    def do_read(self, length, **kwargs):
        return self.sock.recv(length, **kwargs)

    def do_write(self, buf, **kwargs):
        return self.sock.send(buf, **kwargs)


class TimerEvent(BaseEvent):
    """Event for timers"""
    def run_timer(self):
        """this is called when a write event fires in the eventloop.

        Override this in child classes to alter behaviour
        """
        pass

