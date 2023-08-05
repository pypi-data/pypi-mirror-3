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
from ..psifas_exceptions import EndOfStreamException

import select
from io import BytesIO
from os import SEEK_END, SEEK_SET

class PsifasStream(Pretty):
    __slots__ = ['stream', '_read_func', 'start_offset', 'size']
    def __init__(self, stream):
        super(PsifasStream, self).__init__()
        if isinstance(stream, bytes):
            stream = BytesIO(stream)
        self.stream = stream
        if hasattr(stream, 'read'):
            self._read_func = stream.read
        else:
            self._read_func = self._read_socket
            
        self.size = None
        if hasattr(stream, 'tell') and hasattr(stream, 'seek'):
            self.start_offset = stream.tell()
            stream.seek(-1, SEEK_END)
            self.size = stream.tell() + 1 - self.start_offset
            stream.seek(self.start_offset, SEEK_SET)

    def _read_socket(self, size = 1):
        if size == 0:
            return ''
        while True:
            result = self.stream.recv(size)
            if result != '':
                break
            # poll the socket
            readable_sockets, _, _ = select.select([self.stream], [], [], timeout = 0)
            if self.stream in readable_sockets:
                # the socket is readable, yet the last recv returned an empty string
                # - it must have been closed on the other side.
                break
        return result

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def read(self, size, best_effort = False):
        first_part = self.stream.read(size)
        size -= len(first_part)
        all_parts = []
        while size > 0:
            # usually doesn't happen
            new_part = self.stream.read(size)
            if new_part == '':
                if best_effort:
                    break
                # seek back? self.stream.seek(-len(first_part) - sum(map(len, all_parts)), SEEK_CUR)
                raise EndOfStreamException()
            size -= len(new_part)
        return first_part + ''.join(all_parts)

    def read_all(self):
        all_parts = [self.stream.read()]
        new_part = self.stream.read()
        while new_part != '':
            all_parts.append(new_part)
            new_part = self.stream.read()
        return ''.join(all_parts)

    def __deepcopy__(self, memo):
        return self


            
