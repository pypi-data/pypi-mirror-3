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

from abstract import TopClass, Default, Top
from deque import deque
from ..imerge import imerge_unwrapped
from ..recursion_lock import recursion_lock

class Container(TopClass):
    top_hierarchy = 3
    
    def __init__(self, *args, **kw):
        self.__dict__['_Container__fields_order'] = deque()
        super(Container, self).__init__()
        for name, value in args:
            setattr(self, name, value)
        for name, value in sorted(kw.iteritems()):
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if not self.__dict__.has_key(name):
            self.__fields_order.append(name)
        super(Container, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self.__fields_order:
            self.__fields_order.remove(name)
        super(Container, self).__delattr__(name)

    def imerge(self, other):
        if not isinstance(other, Container):
            return super(Container, self).imerge(other)
        if self is other:
            return self, False
        change_flag = False
        for field in other.__fields_order:
            sub_value, sub_flag = imerge_unwrapped(getattr(self, field, Top),
                                                   getattr(other, field))
            if sub_flag:
                setattr(self, field, sub_value)
                change_flag = True
        return self, change_flag

    def iter_fields(self):
        order = self.__fields_order
        for field in order:
            yield field, getattr(self, field)

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Container):
            return super(Container, self) == other
        sorted_fields = sorted(self.__fields_order)
        if sorted_fields != sorted(other.__fields_order):
            return False
        return self.eq_fields(other, sorted_fields)

    @recursion_lock(lambda self, other, fields: True)    
    def eq_fields(self, other, sorted_fields):
        return all(getattr(self, field) == getattr(other, field) for field in sorted_fields)

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join({False: '%s = %r', True: '%s = %s'}[isinstance(value, Container)] % (name, value)
                           for name, value in self.iter_fields() if not name.startswith('_')))

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join('%s = %r' % (name, value) for (name, value) in self.iter_fields() if not name.startswith('__')))

class DefaultContainer(Container):
    def __getattr__(self, name):
        return getattr(super(DefaultContainer, self), name, Default)
