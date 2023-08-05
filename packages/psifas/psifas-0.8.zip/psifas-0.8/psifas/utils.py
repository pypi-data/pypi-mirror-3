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

from datatypes.abstract import Top
from psifas_exceptions import DereferenceException

from datatypes.deque import deque
from datatypes.singleton import Singleton
from itertools import izip, izip_longest, tee
from weakref import WeakValueDictionary

from itertools import count

unique_id_counter = count() # FEATURE: use random for the initial value to avoid unpickling id reuse?
    

if not hasattr(__builtins__, 'next'):
    def next(iterator, *args):
        # args should have 0 or 1 arguments
        try:
            iterator.next(*args[1:])
        except StopIteration:
            if len(args) == 0:
                raise
            return args[0]

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def pairwise_longest(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip_longest(a, b)
    
    
class Finished(Singleton):
    def __iadd__(self, other):
        return self

class Path(object):
    __slots__ = ['_elements', '__weakref__']

    # This deque exists inorder to keep the last 10**4 paths "alive", even
    # if noone holds their instance. This makes their recreation faster.
    _last_paths = deque(maxlen = 10**4)

    _from_string = WeakValueDictionary()
    _from_elements = WeakValueDictionary()

    _special_elements = frozenset(('', '.', '..', '...'))

    @property
    def elements(self):
        return self._elements

    @classmethod
    def _from_simplified_elements(cls, elements):
        """
        This constructor simply creates a new instance, without
        updating the maps (_from_string, _from_elements).

        Assumes elements is a tuple.
        """
        instance = super(Path, cls).__new__(cls)
        instance._elements = elements
        cls._last_paths.append(instance)
        return instance

    @classmethod
    def _simplify(cls, elements):
        parent_level = 0
        simplified_elements = []
        for element in reversed(elements):
            if element in cls._special_elements:
                if element == '..':
                    parent_level += 1
                elif element == '...':
                    simplified_elements += ['..'] * parent_level
                    simplified_elements.append('...')
                    parent_level = 0
            elif parent_level > 0:
                parent_level -= 1
            else:
                simplified_elements.append(element)
        simplified_elements += ['..'] * parent_level
        simplified_elements.reverse()
        return simplified_elements

    @classmethod
    def from_elements(cls, elements):
        """
        This constructor tries to retrieve the path from the _from_elements
        mapping. On failure, updates the mapping with the new instance.
        """
        elements = tuple(elements)
        instance = cls._from_elements.get(elements, None)
        if instance is None:
            simplified_elements = tuple(cls._simplify(elements))
            instance = cls._from_elements.get(simplified_elements, None)
            if instance is None:
                cls._from_elements[simplified_elements] = instance = cls._from_simplified_elements(simplified_elements)
            cls._from_elements[elements] = instance
        return instance

    def __new__(cls, path_string=''):
        """
        This constructor tries to retrieve the path from the _from_string
        mapping. On failure, updates the mapping with the new instance.
        """
        instance = cls._from_string.get(path_string, None)
        if instance is None:
            cls._from_string[path_string] = instance = cls.from_elements(path_string.split('/'))
        return instance

    def __deepcopy__(self, memo):
        return self

    def join(self, other):
        """
        This constructor acts like from_elements.
        However, because we know that self._elements and other._elements are already simplified
        we can simplifiy their concatenation in a faster way.
        """
        elements = self._elements + other._elements
        instance = self._from_elements.get(elements, None)
        if instance is None:
            # a faster way to simplify the sum
            index = 0
            for index, (parent, other_element) in enumerate(izip(reversed(self._elements), other._elements)):
                if (other_element != '..') or (parent in ('..', '...')):
                    break
            if index > 0:
                simplified_elements = self._elements[:-index] + other._elements[index:]
                instance = self._from_elements.get(simplified_elements, None)
                if instance is None:
                    self._from_elements[simplified_elements] = instance = self._from_simplified_elements(simplified_elements)
            else:
                # already simplified
                instance = self._from_simplified_elements(elements)
        self._from_elements[elements] = instance
        return instance

    def to_string(self):
        return ('/'.join(self._elements)) or '.'

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.to_string())

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Path):
            return super(Path, self) == other
        return self._elements == other._elements
    
    def __hash__(self):
        return hash(self._elements)

class Link(Path):
    _from_string = WeakValueDictionary()
    _from_elements = WeakValueDictionary()
    
    def is_broken(self, context):
        try:
            if context.sub_context(self).value is not Top:
                return False
        except DereferenceException:
            pass
        return True



