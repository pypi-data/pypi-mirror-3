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

from recursion_lock import recursion_lock
from utils import Path, unique_id_counter

class Location(object):
    """
    In this partial class _context is not set.
    When TopLocation is initialized, it creates a new Context.
    When Location is initialized, it creates a sub-context from its parent.
    """
    __slots__ = ['parent', 'index', 'full_name', '_context',
                 'children', 'id']
    def __init__(self, index, full_name, parent):
        super(Location, self).__init__()

        # assert '/' not in full_name
        # assert full_name not in ('', '..')

        self.parent = parent
        self.index = index
        self.full_name = full_name
        # self._context = context

        self.children = []
        self.id = unique_id_counter.next()

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, value):
        self.children[key] = value

    def __delitem__(self, key):
        del self.children[key]

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def engine(self):
        return self.direct_context().engine

    def extend(self, value):
        return self.children.extend(value)

    def append(self, value):
        return self.children.append(value)

    def create_sublocations(self, creator, fields):
        """
        If the sub-locations do not exist - automatically creates them.
        """
        current_len = len(self)
        if current_len < len(fields):
            # adds the new fields
            self.extend(field.create_sublocation(creator, self, current_len + index)
                        for index, field in enumerate(fields[current_len:]))

    def add_sublocations(self, creator, fields):
        """
        forces an addition of the sublocations
        """
        current_len = len(self)
        self.extend(field.create_sublocation(creator, self, current_len + index)
                    for index, field in enumerate(fields))

    def iter_names(self):
        """
        iterator on the sub_locations' names
        """
        return (sub_location.full_name for sub_location in self)

    def names(self):
        """
        returns a list of the sub-locations' names
        """
        return list(self.iter_names())

    def __repr__(self):
        return '%s(/%s)' % (self.__class__.__name__,
                            '/'.join('%s:%s' % (parent.index, parent.full_name)
                                     for parent in self.parent_stack()[1:]))

    @recursion_lock(lambda self: '%s(%r, ...)' % (self.__class__.__name__, self.full_name))
    def __str__(self):
        return '%s(%r)' % (self.__class__.__name__, self.full_name)

    def find_iter(self, full_name):
        """
        finds the sub-locations with the given name
        """
        for sub_location in self:
            if sub_location.full_name == full_name:
                yield sub_location

    def find(self, full_name):
        return list(self.find_iter(full_name))

    def payload_context(self):
        return self.context('.payload#%d' % (self.id,))

    def payload_offset_context(self):
        return self.context('.payload_offset#%d' % (self.id,))
        
    def context(self, rel_path_str = '.'):
        return self.direct_context().sub_context(Path(rel_path_str))

    # and without following links:

    def direct_payload_context(self):
        return self.direct_context().get_child('.payload#%d' % (self.id,))

    def direct_payload_offset_context(self):
        return self.direct_context().get_child('.payload_offset#%d' % (self.id,))

    def direct_context(self):
        while self._context.replacer is not None:
            # FEATURE: prevent infinite loop?
            self._context = self._context.replacer
        return self._context

    def parent_stack(self):
        stack = [self]
        current = self.parent
        while current is not None:
            stack.append(current)
            current = current.parent
        stack.reverse()
        return stack
                                 
    def top_parent(self):
        current = self
        while current.parent is not None:
            current = current.parent
        return current

    def _tree(self, indent_string = '   '):
        yield self.direct_context().display(self.full_name)
        if self.direct_context().link is not None:
            return
        yield indent_string + self.direct_payload_offset_context().display('.payload_offset#%d' % (self.id,))
        yield indent_string + self.direct_payload_context().display('.payload#%d' % (self.id,))
        for sub_location in self.children:
            for line in sub_location._tree(indent_string):
                yield indent_string + line

    def tree(self, indent_string = '   '):
        return '\n'.join(self._tree(indent_string))
                          
        

