from __future__ import print_function, unicode_literals

import errno

def print_lines(fn):
    def wrapped(*args, **kwargs):
        name = fn.__name__.lower()
        if name.startswith('read'):
            start = '>'
        elif name.startswith('write'):
            start = '<'
        else:
            start = '-'

        print(start, fn(*args, **kwargs).rstrip('\n'))
    return wrapped

