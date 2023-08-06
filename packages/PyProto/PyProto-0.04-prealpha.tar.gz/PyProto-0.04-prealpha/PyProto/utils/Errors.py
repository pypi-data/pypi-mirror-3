import errno

ignore_errnos = ('EAGAIN', 'EINPROGRESS', 'EINTR', 'ERESTART', 'ENOBUFS', 'ENOENT', 'WSAEWOULDBLOCK', 'WSAENOBUFS', 'WSAEINPROGRESS', 'WSAEINTR')

def ignore_errno(errorcode):
    if errorcode not in errno.errorcode:
        return False

    if errno.errorcode[errorcode] in ignore_errnos:
        return True

    return False

class PyProtoException(Exception):
    """ Base PyProto Exception class """

