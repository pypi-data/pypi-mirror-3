from PyProto.eventloop import Exceptions
from PyProto.eventloop.Events import EVENT_IN, EVENT_OUT, EVENT_EXCEPT
from PyProto.eventloop.engines import nullengine

try: from select import EPOLLIN, EPOLLOUT, EPOLLERR, epoll
except: raise Exceptions.EventLoopUnsupportedException("epoll is only supported on Linux 2.5.x and above.")

class EpollEventEngine(nullengine.NullEventEngine):
    def __init__(self):
        # Initalise some internal state
        self.epollhandle = epoll()

    def __flags_to_epoll(self, evtype):
        mask = 0
        if evtype & EVENT_IN != 0:
            mask |= EPOLLIN
        if evtype & EVENT_OUT != 0:
            mask |= EPOLLOUT
        if evtype & EVENT_EXCEPT != 0:
            mask |= EPOLLERR

        return mask

    def register_fd(self, fd, evtype):
        mask = self.__flags_to_epoll(evtype)
        self.epollhandle.register(fd, mask)
    
    # Obliterate FD entirely
    def unregister_fd(self, fd):
        self.epollhandle.unregister(fd)

    def modify_fd(self, fd, evtype):
        mask = self.__flags_to_epoll(evtype)
        self.epollhandle.modify(fd, mask)

    def run_once(self, timeout=-1.0):
        # It *needs* a float.
        if timeout == 0 or timeout is None:
            timeout = -1.0
        elif isinstance(timeout, int):
            timeout = float(timeout)

        fds = self.epollhandle.poll(timeout)

        fdlist = []

        for s in fds:
            fd, event = s

            mask = 0
            if event & EPOLLIN != 0:
                mask |= EVENT_IN 
            if event & EPOLLOUT != 0:
                mask |= EVENT_OUT
            if event & EPOLLERR != 0:
                mask |= EVENT_EXCEPT

            fdlist.append((fd, mask))

        return fdlist

