# Copyright (C) 2011 Oren Zomer <oren.zomer@gmail.com>

#                          *** MIT License ***
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pretty import Pretty
from psifas_stream import PsifasStream
from ..psifas_exceptions import EndOfStreamException

from itertools import count, izip
import abc
import weakref
from sys import maxint
from copy import deepcopy


class MetaSequence(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __len__(self):
        """
        all inheriting classes must have __len__
        """
        return NotImplemented

class MetaTuple(MetaSequence):
    pass
MetaTuple.register(tuple)

class MetaList(MetaSequence):
    pass
MetaList.register(list)

class MetaBytes(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __len__(self):
        """
        all inheriting classes must have __len__
        """
        return NotImplemented
    
MetaBytes.register(bytes)
    
try:
    import blist
    MetaTuple.register(blist.btuple)
    MetaList.register(blist.blist)
    optimized_tuple = blist.btuple
    optimized_list = blist.blist
    sortedlist = blist.sortedlist
    sortedset = blist.sortedset
except ImportError:
    optimized_tuple = tuple
    optimized_list = list
    # TODO: verify that sortedlist works (implement all required functions)
    import bisect as _bisect
    class sortedlist(list):
        def __init__(self, values = (), key = None):
            super(sortedlist, self).__init__(values)
            self.sort(key = key)

        def bisect_left(self, *args):
            return _bisect.bisect_left(self, *args)

        def bisect_right(self, *args):
            return _bisect.bisect_right(self, *args)

        def bisect(self, *args):
            return _bisect.bisect(self, *args)

        def add(self, *args):
            return _bisect.insort(self, *args)

        def update(self, items):
            for item in items:
                self.add(item)
            
    class sortedset(object):
        class _sortedset_item_wrapper(object):
            def __init__(self, wrapped, key = None):
                self.key = key if key is not None else (lambda x: x)
                self.wrapped = wrapped
                
            def __cmp__(self, other):
                return cmp(self.key(self), self.key(other))
        
        def __init__(self, values = (), key = None):
            super(sortedset, self).__init__()
            self.items = sortedlist((self._sortedset_item_wrapper(value) for value in set(values)))
            self._key = key

        def __len__(self):
            return len(self.items)

        def __iter__(self):
            for item in self.items:
                yield item.wrapped
            
        def add(self, item):
            wrapped = _sortedset_item_wrapper(item, key = self._key)
            item_index = self.items.bisect_left(wrapped)
            if item_index >= len(self) or self.items[item_index] != wrapped:
                self.items.add(wrapped)

        def discard(self, item):
            wrapped = _sortedset_item_wrapper(item, key = self._key)
            item_index = self.items.bisect_left(wrapped)
            if item_index < len(self) and self.items[item_index] == wrapped:
                del self.items[item_index]
                
        def __getitem__(self, key):
            if isinstance(key, slice):
                return [wrapper.wrapped for wrapper in self.items[key]]
            return self.items[key].wrapped

        def pop(self, index = -1):
            return self.items.pop(index).wrapped

        def __delitem__(self, key):
            del self.items[key]

        def __ior__(self, items):
            for item in items:
                self.add(item)
            

def sequence_sum(a, b):
    if (isinstance(a, MetaTuple) and isinstance(b, MetaTuple)) or \
       (isinstance(a, MetaList) and isinstance(b, MetaList)) or \
       (isinstance(a, MetaBytes) and isinstance(b, MetaBytes)):
        return a + b
    return optimized_tuple(a) + optimized_tuple(b)


class DummyPayloadParent(Pretty):
    # FEATURE: think about keeping a map between every stream and its DummyPayloadParent (In order
    # to prevent from 2 parents using the same stream).
    def __init__(self, stream, payload = ''):
        super(DummyPayloadParent, self).__init__()
        self.stream = stream # should be PsifasStream
        self.payload = payload
        self.finished = False
        self.children = weakref.WeakKeyDictionary()
        self.minimal_absolute_offset = 0

    def __deepcopy__(self, memo):
        # avoid 2 parents with the same stream (which cannot be deepcopied)
        return self

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.stream)

    def __len__(self):
        if self.stream.size is not None:
            return self.stream.size
        return maxint

    def read_until(self, index, best_effort = False):
        """
        reads until the payload has the required length
        """
        if len(self.payload) < index + 1:
            try:
                self.payload += self.stream.read(index + 1 - len(self.payload), best_effort = best_effort)
            except EndOfStreamException, e:
                self.finished = True
                raise IndexError("Cannot evaluate dummy-payload-parent at given index", index, e)
        return self.payload[:index + 1]

    def read_all(self):
        self.payload += self.stream.read_all()
        self.finished = True
        return self.payload

    def clean(self):
        new_minimal_absolute_offset = min([self.minimal_absolute_offset + len(self.payload)] + 
                                          [child.absolute_offset for child in self.children.iterkeys()])
        bytes_to_remove = new_minimal_absolute_offset - self.minimal_absolute_offset
        if bytes_to_remove > 0:
            self.payload = self.payload[bytes_to_remove:]
            self.minimal_absolute_offset = new_minimal_absolute_offset
        return bytes_to_remove
        

class DummyPayload(Pretty):
    def __new__(cls, stream, payload = ''):
        if not isinstance(stream, PsifasStream):
            stream = PsifasStream(stream)
        return cls.from_parent(DummyPayloadParent(stream, payload), 0)

    def __deepcopy__(self, memo):
        instance = memo.get(self, None)
        if instance is not None:
            return instance
        memo[self] = instance = super(DummyPayload, self).__new__(self.__class__)
        instance.parent = deepcopy(self.parent, memo)
        instance.absolute_offset = deepcopy(self.absolute_offset, memo)
        instance.prefix = deepcopy(self.prefix, memo)
        return instance

    @classmethod
    def from_parent(cls, parent, absolute_offset, prefix = ''):
        assert absolute_offset >= parent.minimal_absolute_offset, "Trying to create a DummyPayload on a slice that the DummyParentPayload forgot"
        instance = super(DummyPayload, cls).__new__(cls)
        instance.parent = parent
        instance.absolute_offset = absolute_offset
        instance.prefix = prefix
        # the parent remembers its children with a weak reference
        parent.children[instance] = None
        if parent.finished:
            return str(instance)
        return instance

    def offset(self):
        """
        returns the relative offset in the parent's payload.
        """
        return self.absolute_offset - self.parent.minimal_absolute_offset

    def __str__(self):
        return self._read_all()

    __repr__ = Pretty.__repr__

    def _read_until(self, index):
        if index >= len(self.prefix):
            return self.prefix + self.parent.read_until(self.offset() - len(self.prefix) + index, best_effort = True)[self.offset():]
        return self.prefix[:index + 1]

    def _read_all(self):
        return self.prefix + self.parent.read_all()[self.offset():]

    def __del__(self):
        self.parent.clean()

    def __len__(self):
        return len(self.prefix) + len(self.parent) - self.offset()

    def __cmp__(self, other):
        if isinstance(other, DummyPayload):
            self_payload = self._payload()
            other_payload = other._payload()
            min_payload_length = min(len(self_payload), len(other_payload))
            prefix_compare = cmp(self_payload[:min_payload_length], other_payload[:min_payload_length])
            if prefix_compare != 0:
                return prefix_compare
            if self.prefix == other.prefix and self.parent == other.parent and self.offset() == other.offset():
                return 0
        if isinstance(other, MetaBytes):
            return cmp(self._read_until(len(other)), other)
        return str.__cmp__(self, other)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start
            step = key.step
            stop = key.stop

            if step is None:
                step = 1
            elif step == 0:
                raise ValueError("slice step cannot be zero", key)
            
            if step < 0:
                if (start is None) or (start < 0):
                    return self._read_all()[key]
                return self._read_until(start)[key]
            
            # step > 0
            if stop is not None:
                if (stop < 0) or ((start is not None) and (start < 0)):
                    return self._read_all()[key]
                return self._read_until(stop - step)[key]
            
            # stop is None
            if step != 1:
                return self._read_all()[key]
            
            if start is None:
                start = 0
            elif start < 0:
                return self._read_all()[key]
            if start < len(self.prefix):
                return self.from_parent(self.parent, self.absolute_offset, self.prefix[start:])
            return self.from_parent(self.parent, self.absolute_offset + start - len(self.prefix))
        if key < 0:
            return self._read_all()[key]
        return self._read_until(key)[key]

    def __iter__(self):
        for index in count():
            try:
                yield self[index]
            except IndexError:
                break

    def __add__(self, other):
        if isinstance(other, bytes) or isinstance(other, DummyPayload):
            return self._read_all() + other
        # In SparseString - the _read_all is called from the SparseString.__radd__
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.from_parent(self.parent, self.absolute_offset, other + self.prefix)
        return NotImplemented

    def _payload(self):
        """
        returns the already read payload.
        """
        return self.prefix + self.parent.payload[self.offset():]

    def startswith(self, other):
        return self[:len(other)] == other

MetaBytes.register(DummyPayload)


def str_wrapper(func):
    def new_func(self, *args, **kws):
        return func(bytes(self), *args, **kws)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    return new_func

for attr in dir(bytes):
    if attr in ('__class__', '__getattribute__', '__setattr__', '__init__', '__new__', '__getslice__'):
        continue
    if not hasattr(DummyPayload, attr):
        setattr(DummyPayload, attr, str_wrapper(getattr(str, attr)))
            
        
def length_compare(a, b):
    if not isinstance(a, DummyPayload):
        if not isinstance(b, DummyPayload):
            return cmp(len(a), len(b))
        return cmp(len(a), len(b[:len(a) + 1]))
    elif not isinstance(b, DummyPayload):
        return cmp(len(a[:len(b) + 1]), len(b))
    assert hasattr(a, '__len__') or hasattr(b, '__len__'), "length_compare was called on limitless objects: %r, %r" % (a, b)
    a_iter = iter(a)
    b_iter = iter(b)
    for couple in izip(a_iter, b_iter):
        pass
    try:
        a_iter.next()
        return 1
    except StopIteration:
        pass
    try:
        b_iter.next()
        return -1
    except StopIteration:
        pass
    return 0
