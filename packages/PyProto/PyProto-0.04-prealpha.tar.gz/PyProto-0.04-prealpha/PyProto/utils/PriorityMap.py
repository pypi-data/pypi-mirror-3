import bisect
from collections import MutableMapping, defaultdict
import time

class PriorityMap(MutableMapping):
    """ Priority mapping class that supports key:value pairs, with a few
    twists:

    - Keys are returned in sorted order (sorted list is kept for speed)
    - Supports retrieving keys matching a specified operator and then
      removing them after iteration.
    - Works as a multimap and normal mapping :)
 
    Caveats:
    - All keys must be of mutually comparable types

    >>> from PriorityMap import PriorityMap
    >>> m = PriorityMap()
    >>> m[1] = 'test'
    >>> m
    {1 :['test']}
    >>> m[1] = 'test2'
    >>> m
    {1 :['test2']}
    >>> m.additem(1, 'test3')
    >>> m
    {1 :['test2', 'test3']}
    >>> m.additem('strkey', 'test')
    Traceback (most recent call last):
        ...
    TypeError: unorderable types: str() < int()
    >>> m.additem(8, 'foo')
    >>> m
    {1 :['test2', 'test3'], 8 :['foo']}
    >>> m.additem(4, 'bar')
    >>> m.additem(4, 'baz')
    >>> m.additem(16, 'frob')
    >>> m
    {1 :['test2', 'test3'], 4 :['bar', 'baz'], 8 :['foo'], 16 :['frob']}
    >>> m.delitem(4, 'bar')
    >>> m
    {1 :['test2', 'test3'], 4 :['baz'], 8 :['foo'], 16 :['frob']}
    >>> import operator
    >>> [(k, m[k]) for k in m.keys_matching(6, operator.lt, delete=False)]
    [(1, ['test2', 'test3']), (4, ['baz'])]
    >>> m
    {1 :['test2', 'test3'], 4 :['baz'], 8 :['foo'], 16 :['frob']}
    >>> [(k, m[k]) for k in m.keys_matching(6, operator.lt, delete=True)]
    [(1, ['test2', 'test3']), (4, ['baz'])]
    >>> m
    {8 :['foo'], 16 :['frob']}

    """
    def __init__(self, keytype=None):
        self.valuemap = defaultdict(list) # Our actual mapping :p. 
        self.keyheap = list() # Sorted keys list for fast retrieval
        self.keytype = keytype
        self.len_all = 0

    def __getitem__(self, key):
        return self.valuemap[key]
    
    def __setitem__(self, key, value):
        if key not in self.keyheap:
            bisect.insort_right(self.keyheap, key)
        
        self.valuemap[key] = [value]
        self.len_all += 1

    def __delitem__(self, key):
        self.len_all -= len(self.valuemap[key])
        del self.valuemap[key]
        self.keyheap.remove(key)

    def __iter__(self):
        for item in self.keyheap:
            yield item

    def __len__(self):
        return len(self.valuemap)

    def __repr__(self):
        ilist = list()
        for key, value in self.items():
            ilist.append('{} :{}'.format(repr(key), repr(value)))

        return '{%s}' % ', '.join(ilist)

    def additem(self, key, value):
        if self.keytype is not None and type(key) != self.keytype:
            raise KeyError("Keys must be of type %s" % self.keytype)

        if key not in self.keyheap:
            bisect.insort_right(self.keyheap, key)
        self.valuemap[key].append(value)
        self.len_all += 1

    def delitem(self, key, value):
        if key not in self.valuemap:
            raise KeyError

        self.valuemap[key].remove(value)
        self.len_all -= 1

        if len(self.valuemap[key]) == 0:
            self.__delitem__(key)

    def keys_matching(self, key, operator, delete=True):
        rmset = set()
        for k in self.keyheap:
            if not operator(k, key):
                break
        
            yield k
            rmset.add(k)

        if not delete:
             return

        for k in rmset:
            self.__delitem__(k)
