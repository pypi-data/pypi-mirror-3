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

class _singleton_metaclass(type):
    def __new__(mcs, name, bases, namespace):
        """
        instead of returning the new type, it returns a new instance of the new type.
        """
        return type.__new__(mcs, name, bases, namespace)()

class _singleton_main_metaclass(type):
    def __new__(mcs, name, bases, namespace):
        """
        The subclasses of this class will use _singleton_metaclass
        """
        return type.__new__(_singleton_metaclass, name, bases, namespace)

class Singleton(object):
    __metaclass__ = _singleton_main_metaclass

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        """
        makes it pickleable
        """
        return self.__class__.__name__
