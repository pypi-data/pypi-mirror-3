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

from singleton import Singleton
from dummy import MetaSequence, MetaBytes
from ..psifas_exceptions import MergeException

import abc
import numbers

class Abstract(object):
    def is_abstract(self, next_args):
        return True

    def concrete(self):
        """
        tries to get a more concrete value
        """
        if is_abstract(self):
            return self
        return self._concrete()
    
    def _concrete(self):
        return self

def is_abstract(*args):
    scanned_seqs = []
    while len(args) > 0:
        next_args = []
        for arg in args:
            if isinstance(arg, Abstract) and arg.is_abstract(next_args):
                return True
            if isinstance(arg, MetaSequence) and not isinstance(arg, MetaBytes) and \
               not any(arg is seq for seq in scanned_seqs):
                scanned_seqs.append(arg)
                next_args.extend(arg)
        args = next_args
    return False

class TopClass(Abstract):
    top_hierarchy = 0

    def _top_key(self):
        return (self.top_hierarchy, self)
    
    def imerge(self, other):
        if not isinstance(other, TopClass):
            return other, True
        better = max(self, other, key = TopClass._top_key)
        return better, better is other

class Top(Singleton, TopClass):
    __slots__ = []

    top_hierarchy = 1

    def __nonzero__(self):
        return False
    # for python3:
    __bool__ = __nonzero__

class Default(Singleton, TopClass):
    """
    The difference between Top, AcceptAll, and Default is in the parsing-dependency.
    When the _parse function returns Top, it means that it failed to calculate what it needs,
    and if it keeps happening with incrementation of 'process', an exception will be raised on
    'missing dependencies'.
    When the _parse function returns AcceptAll, it means that the calculation has finished, but
    nothing will be put in the context. Therefore other Psifases that depend on this context may
    not be executed until someone else puts a real value in that context - the context stays
    with Top.
    When the _parse function returns Default, the context's value is filled with Default. This
    value can dumb-merge with any other value. The other Psifases will be fully executed, and
    will se the value Default in that context.
    """
    __slots__ = []
    
    top_hierarchy = 2

Ignore = Default

class AcceptAll(Singleton, TopClass):
    # top_hirerchy is 0 - never will be merged into any context value,
    # because they start with "Top".
    pass

class NumberAbstraction(Singleton, Abstract):
    def imerge(self, other):
        if isinstance(other, numbers.Number):
            return other, True
        raise MergeException("The value is not a number", other)

    def rimerge(self, other):
        if isinstance(other, numbers.Number):
            return other, False
        raise MergeException("The value is not a number", other)

class CharAbstraction(Singleton, Abstract):
    def imerge(self, other):
        if isinstance(other, MetaBytes) and len(other) == 1:
            return other, True
        raise MergeException("The value is not a char", other)

    def rimerge(self, other):
        if isinstance(other, MetaBytes) and len(other) == 1:
            return other, False
        raise MergeException("The value is not a char", other)
        
class StringAbstraction(object):
    __metaclass__ = abc.ABCMeta
    
    def length_range(self):
        if isinstance(self, MetaBytes):
            return (len(self),) * 2
        return self.length_range()

    def __init__(self):
        raise TypeError('Cannot create StringAbstraction object - use SparseString')
    
StringAbstraction.register(MetaBytes)
    
class SequenceAbstraction(object):
    __metaclass__ = abc.ABCMeta
    
    def length_range(self):
        if isinstance(self, MetaSequence):
            return (len(self),) * 2
        return self.length_range()

    def __init__(self):
        raise TypeError('Cannot create SequenceAbstraction object - use SparseSequence')
    
SequenceAbstraction.register(MetaSequence)
