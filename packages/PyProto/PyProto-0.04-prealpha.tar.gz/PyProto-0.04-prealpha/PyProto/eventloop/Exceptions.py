from PyProto.utils import Errors

class EventLoopException(Errors.PyProtoException):
    """Exception used when the event loop has an error"""

class EventLoopUnsupportedException(EventLoopException):
    """Unsupported eventloop type!"""

class EventException(Errors.PyProtoException):
        """Exception used when an event has an error"""
