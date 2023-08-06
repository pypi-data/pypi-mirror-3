from PyProto.eventloop import Exceptions
from PyProto.eventloop.Events import EVENT_IN, EVENT_OUT, EVENT_EXCEPT
from PyProto.eventloop.engines import nullengine

try: from select import select 
except: raise Exceptions.EventLoopUnsupportedException("select is not supported on your platform.")

class SelectEventEngine(nullengine.NullEventEngine):
    def __init__(self):
        # :(
        self.fdlist = {}

    def register_fd(self, fd, evtype):
        self.fdlist[fd] = evtype

    def modify_fd(self, fd, evtype):
        self.fdlist[fd] = evtype

    def unregister_fd(self, fd):
        if fd in self.fdlist:
            del self.fdlist[fd]

    def run_once(self, timeout=None):
        if timeout == 0:
            timeout = None

        # Build the lists
        infds = list()
        outfds = list()
        exceptfds = list()

        for fd, mask in self.fdlist.items():
            if mask & EVENT_IN != 0:
                infds.append(fd)
            if mask & EVENT_OUT != 0:
                outfds.append(fd)
            if mask & EVENT_EXCEPT != 0:
                exceptfds.append(fd)

        ins, outs, excepts = select(infds, outfds, exceptfds, timeout)

        fdlist = [(fd, EVENT_IN) for fd in ins]
        
        # Aggregate
        for fd in outs:
            if fd in fdlist:
                index = fdlist.index(fd)
                fdlist[index] = (fd, fdlist[index][1] | EVENT_OUT)
            else:
                fdlist.append((fd, EVENT_OUT))

        for fd in excepts:
            if fd in fdlist:
                index = fdlist.index(fd)
                fdlist[index] = (fd, fdlist[index][1] | EVENT_EXCEPT)
            else:
                fdlist.append((fd, EVENT_EXCEPT))

        return fdlist

