from PyProto.eventloop import Exceptions
from PyProto.eventloop.Events import EVENT_IN, EVENT_OUT, EVENT_EXCEPT
from PyProto.eventloop.engines import nullengine

try: from select import POLLIN, POLLOUT, POLLERR, poll
except: raise Exceptions.EventLoopUnsupportedException("poll is not supported on your platform.")

class PollEventEngine(nullengine.NullEventEngine):
    def __init__(self):
        # Initalise some internal state
        self.pollhandle = poll()

    def __flags_to_poll(self, evtype):
        mask = 0
        if evtype & EVENT_IN:
            mask |= POLLIN
        if evtype & EVENT_OUT:
            mask |= POLLOUT
        if evtype & EVENT_EXCEPT:
            mask |= EVENT_EXCEPT

        return mask

    def register_fd(self, fd, evtype):
        mask = self.__flags_to_poll(evtype)
        self.pollhandle.register(fd, mask)

    def modify_fd(self, fd, evtype):
        mask = self.__flags_to_poll(evtype)
        self.pollhandle.modify(fd, mask)

    def unregister_fd(self, fd):
        self.pollhandle.unregister(fd)

    def run_once(self, timeout=None):
        if timeout == 0:
            timeout = None

        fds = self.pollhandle.poll(timeout)

        fdlist = []

        for s in fds:
            fd, event = s

            mask = 0
            if event & POLLIN != 0:
                mask |= EVENT_IN 
            if event & POLLOUT != 0:
                mask |= EVENT_OUT
            if event & POLLERR != 0:
                mask |= EVENT_EXCEPT

            fdlist.append((fd, mask))

        return fdlist

