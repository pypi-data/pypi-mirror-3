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

from collections import deque as _deque

try:
    _deque(maxlen=1)
except TypeError:
    class LimitedDeque(_deque):
        def __init__(self, iterable, maxlen):
            _deque.__init__(self, iterable)
            self.__maxlen = maxlen
            
        def appendleft(self, *args, **kw):
            try:
                return _deque.appendleft(self, *args, **kw)
            finally:
                if len(self) > self.__maxlen:
                    _deque.pop(self)

        def extendleft(self, var):
            try:
                return _deque.extendleft(self, var)
            finally:
                while len(self) > self.__maxlen:
                    _deque.pop(self)
            
        def append(self, *args, **kw):
            try:
                return _deque.append(self, *args, **kw)
            finally:
                if len(self) > self.__maxlen:
                    _deque.popleft(self)

        def extend(self, var):
            try:
                return _deque.extend(self, var)
            finally:
                while len(self) > self.__maxlen:
                    _deque.popleft(self)

    def deque(iterable = (), maxlen = None):
        if maxlen is None:
            return _deque(iterable)
        return LimitedDeque(iterable, maxlen)
else:
    deque = _deque
