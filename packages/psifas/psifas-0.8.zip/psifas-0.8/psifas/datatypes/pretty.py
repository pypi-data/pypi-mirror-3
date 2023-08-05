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

from ..recursion_lock import recursion_lock
import re

MIN_NEW_LINE_LENGTH = 7

class Pretty(object):
    def _dict(self):
        slots = getattr(self, '__slots__', None)
        if slots is None:
            return self.__dict__
        return dict((slot, getattr(self, slot)) for slot in slots if hasattr(self, slot))
        
    def _pretty_attributes(self):
        """
        should return the attributes to be printed and their values
        """
        return sorted(self._dict().iteritems())

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __repr__(self):
        attrs = ('%s = %r' % item for item in self._pretty_attributes())
        return '%s(%s)' % (self.__class__.__name__, ', '.join(attrs))

    def __cmp__(self, other):
        if self is other:
            return 0
        return cmp(type(self), type(other)) or self.cmp_dicts(other)

    @recursion_lock(lambda self, other: 0)
    def cmp_dicts(self, other):
        return cmp(self._dict(), other._dict())

    

_prettify_special_char_re = re.compile(r"""([\s\\\"\'\,\(\)\[\]\{\}])""")

def prettify(string):
    string = str(string)
    indent_stack = [' ' * (len(string) - len(string.lstrip()))]
    total_seq = indent_stack[:] # copy
    last_line_length = len(total_seq[0])
    string_open_token = None    
    
    inner_seq = ['']
    for token in _prettify_special_char_re.split(string.lstrip()):
        if string_open_token is None:
            if token in ('\n', ' '):
                continue
        
        if inner_seq is not None:
            inner_seq[-1] += token
        else:
            total_seq.append(token)

        if string_open_token is not None:
            if string_open_token == token:
                string_open_token = None
            continue

        if token in ('(', '[', '{'):
            if inner_seq is not None:
                joined_inner_seq = ('\n' + indent_stack[-1]).join(inner_seq)
                total_seq.append(joined_inner_seq)
                if '\n' in joined_inner_seq:
                    last_line_length = len(joined_inner_seq) - joined_inner_seq.rfind('\n') - 1
                else:
                    last_line_length += len(joined_inner_seq)
            inner_seq = ['']
            indent_stack.append(' ' * last_line_length)
        elif token in (')', ']', '}'):
            if inner_seq is not None:
                if any(len(part.strip()) > MIN_NEW_LINE_LENGTH for part in inner_seq):
                    # ends as multiline
                    joined_inner_seq = ('\n' + indent_stack[-1]).join(inner_seq)
                else:
                    # ends as uniline
                    joined_inner_seq = ' '.join(inner_seq)
                total_seq.append(joined_inner_seq)
                if '\n' in joined_inner_seq:
                    last_line_length = len(joined_inner_seq) - joined_inner_seq.rfind('\n') - 1
                else:
                    last_line_length += len(joined_inner_seq)
                inner_seq = None
            if len(indent_stack) > 1:
                indent_stack.pop(-1)
        elif token == ',':
            if inner_seq is None:
                total_seq.append('\n' + indent_stack[-1])
                last_line_length = len(indent_stack[-1])
            else:
                inner_seq.append('')
        elif token in ('"', '\''):
            string_open_token = token
    if inner_seq is not None:
        total_seq.append(' '.join(inner_seq))
    return ''.join(total_seq).rstrip()
        
    
