from PyProto.eventloop import Exceptions
import abc

class NullEventEngine(object):
    """ Base class for all other event engines """
    @abc.abstractmethod
    def register_fd(self, fd, evtype):
        pass

    @abc.abstractmethod
    def modify_fd(self, fd, evtype):
        pass

    @abc.abstractmethod
    def unregister_fd(self, fd):
        pass

    @abc.abstractmethod
    def run_once(self, timeout=None):
        pass

