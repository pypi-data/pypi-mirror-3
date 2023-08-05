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
from datatypes.ordered_set import OrderedSet
from datatypes.deque import deque
from psifas_exceptions import DecipherException, Contradiction, MergeException, InfiniteRecursionException, DereferenceException
from utils import Path
from imerge import imerge
from datatypes.abstract import Abstract, is_abstract
from recursion_lock import recursion_lock
from constraint import SetContextLinkConstraint

class Context(object):
    __slots__ = ['value', 'value_constraints', 'spiritual', 'children', 'parent_stack', 'link',
                 'value_dependent_constraints', 'concrete_dependent_constraints',
                 'engine', 'replacer', 'is_concrete']

    max_visited_links = 10

    @classmethod
    def _increase_max_visited_links(cls):
        cls.max_visited_links *= 2

    def __init__(self, parent = None):
        super(Context, self).__init__()

        self.value = Top
        self.value_constraints = OrderedSet()
        if parent is not None:
            self.parent_stack = (parent,) + parent.parent_stack
            self.engine = parent.engine
        else:
            self.parent_stack = ()
        self.spiritual = None # can be True, False or None
        self.children = {'.': self}
        self.link = None
        self.value_dependent_constraints = OrderedSet()
        self.concrete_dependent_constraints = OrderedSet()
        self.replacer = None
        self.is_concrete = False

    @classmethod
    def from_value(cls, value):
        context = cls()
        context.value = value
        return context
    
    def register_value_constraint(self, constraint):
        if constraint in self.value_dependent_constraints:
            return
        self.value_dependent_constraints.add(constraint)
        constraint.dependencies.add(self)

    def unregister_value_constraint(self, constraint):
        if constraint not in self.value_dependent_constraints:
            return
        self.value_dependent_constraints.discard(constraint)
        constraint.dependencies.discard(self)

    def register_concrete_constraint(self, constraint):
        if constraint in self.concrete_dependent_constraints:
            return
        self.concrete_dependent_constraints.add(constraint)
        constraint.dependencies.add(self)

    def unregister_concrete_constraint(self, constraint):
        if constraint not in self.concrete_dependent_constraints:
            return
        self.concrete_dependent_constraints.discard(constraint)
        constraint.dependencies.discard(self)

    def set_spiritual(self, spiritual):
        if spiritual is None:
            return
        elif self.spiritual is None:
            self.spiritual = spiritual
        elif self.spiritual != spiritual:
            # they are both not None, and differ
            # import pdb; pdb.set_trace()
            raise DecipherException("%r spiritualism was set to by one location to %r and by another location to %r" % (self, self.spiritual, spiritual), self)

    def get_child(self, name):
        result = self.children.get(name, None)
        if result is None:
            self.children[name] = result = Context(self)
        return result

    def iterkeys(self):
        return self.sub_context(Path('.')).children.iterkeys()

    def move_into(self, target_context):
        target_context.set_spiritual(self.spiritual)
        
        if not hasattr(self, 'value'):
            # import pdb; pdb.set_trace()
            # it's a link copy.
            if not target_context.set_link(self.link):
                self.engine.postponed_constraints.add(SetContextLinkConstraint(target_context, self.link))
            return

        self.set_value(target_context.value)
        
        target_context.set_value(self.value)
        
        target_context.value_constraints |= self.value_constraints
        
        for constraint in self.value_dependent_constraints:
            constraint.dependencies.discard(self)
            constraint.dependencies.add(target_context)
        target_context.value_dependent_constraints |= self.value_dependent_constraints
        
        for constraint in self.concrete_dependent_constraints:
            constraint.dependencies.discard(self)
            constraint.dependencies.add(target_context)
        target_context.concrete_dependent_constraints |= self.concrete_dependent_constraints
        
        for name, sub_context in self.children.iteritems():
            if name == '.':
                continue
            sub_target_context = target_context.sub_context(Path(name))
            sub_context.move_into(sub_target_context)
            sub_context.replacer = sub_target_context
            

    def set_link(self, link):
        if self.link is not None:
            if self.link == link:
                return True
            raise Contradiction("Cannot set a linking context to a different value", self, link, self.engine.running_constraint)
        
        target_context = self.sub_context(link)
        if target_context is None:
            return False
        self.value_constraints.add(self.engine.running_constraint)
            
        self.move_into(target_context)
        # disconnect the context from the tree
        self.link = link
        # to avoid any access to them in the future:
        del self.children
        del self.value
        del self.value_dependent_constraints
        del self.concrete_dependent_constraints
        del self.is_concrete

        return True

    def get_value(self):
        if self.is_concrete:
            # The value is concrete - the constraint will not get better results in the future
            # No reason to unregister - there won't be changes: self.unregister_value_constraint(self.engine.running_constraint)
            pass
        else:
            # The value may become more concrete in the future
            self.register_value_constraint(self.engine.running_constraint)
        return self.value

    def get_is_concrete(self):
        if self.is_concrete:
            # The value is concrete - the constraint will not get better results in the future
            # No reason to unregister - there won't be changes: self.unregister_value_constraint(self.engine.running_constraint)
            return True
        else:
            # The value may become more concrete in the future
            self.register_concrete_constraint(self.engine.running_constraint)
            return False
            
    def set_value(self, value):
        assert self.link is None
        if value is Top:
            return

        # If not already there:
        self.value_constraints.add(self.engine.running_constraint)
            
        try:
            new_value, change_flag = imerge(self.value, value)
            if isinstance(new_value, Abstract):
                con_value = new_value.concrete()
                if con_value is not new_value:
                    change_flag = True
                    new_value = con_value
            if change_flag:
                if not is_abstract(new_value):
                    self.is_concrete = True
                    self.engine.constraints |= self.concrete_dependent_constraints
                self.engine.constraints |= self.value_dependent_constraints
                
                self.engine.change_count += 1
            self.value = new_value
        except MergeException:
            raise Contradiction("old_value %r contradicts new value %r found from %s." %
                                (self.value,
                                 value,
                                 self.engine.running_constraint))

    def _deref(self, visited_links):
        # assert self.link is not None
        if len(visited_links) > self.max_visited_links:
            if self in visited_links:
                raise InfiniteRecursionException("Links point to each other and create infinite dereference loop", self)
            else:
                # the max_visited_links estimation was too low
                self._increase_max_visited_links()
        visited_links.append(self)
        return self._sub_context(self.link, visited_links)

    # the following function do not receive "self" in purpose.

    def _normal_parent(parent_stack, target, element, visited_links):
        return parent_stack.popleft()

    def _spiritual_parent(parent_stack, target, element, visited_links):
        target = parent_stack.popleft()
        while target is not None and target.spiritual is not True:
            if target.spiritual is None:
                raise DereferenceException("failed to find dereference link to spiritual context - spiritualism unknown", parent_stack, target)
            # target.spiritual is False:
            target = parent_stack.popleft()
        return target

    @staticmethod
    def _normal_element(parent_stack, target, element, visited_links):
        parent_stack.appendleft(target)
        
        if target.link is not None:
            target = target._deref(visited_links)
        
        target = target.get_child(element)
        return target

    _sub_context_func = {'..': _normal_parent,
                         '...': _spiritual_parent}

    def sub_context(self, full_path):
        try:
            return self._sub_context(full_path, [])
        except IndexError, e:
            raise DereferenceException("cannot deref to: %s" % (full_path,), e)

    def _sub_context(self, full_path, visited_links):
        target = self
        
        parent_stack = deque(target.parent_stack + (None,))

        for element in full_path.elements:
            target = self._sub_context_func.get(element, self._normal_element)(parent_stack,
                                                                               target,
                                                                               element,
                                                                               visited_links)
            if target is None:
                return None
        if target.link is not None:
            target = target._deref(visited_links)        
        return target
    
    @recursion_lock(lambda indent, indent_string, recursive: "(RECURSION IN TREE!)", exclude = (0, 'indent', 1, 'indent_string'))
    def ls_iter(self, indent_string = '   ', recursive = False):
        """
        Aid function to iterate over the textual format of the child-contexts.
        """
        if not hasattr(self, 'children'):
            yield '<link does not have children>'
            return
        for name, sub_context in sorted(self.children.iteritems()):
            if name == '.':
                continue
            yield indent_string + sub_context.display(name)
            if sub_context.link is None and recursive:
                for line in sub_context.ls_iter(indent_string, recursive):
                    yield indent_string + line

    def display(self, name):
        spiritual_sign = {True: '*', False: '', None: '^'}[self.spiritual]
        if self.link is not None:
            return '%s%s -> %s%s' % (name, spiritual_sign,
                                     self.link.to_string(), ' ???' if len(self.parent_stack) == 0 or self.link.is_broken(self.parent_stack[0]) else '')
        else:
            return '%s%s: %r' % (name, spiritual_sign, self.value)

    def ls(self, indent_string = '   ', recursive = False):
        """
        Aid function to return a tuple of the textual format of the child-contexts.
        If you want a recurisve ls without indentations, use indent_string = ''.
        """
        return tuple(self.ls_iter(indent_string = indent_string, recursive = recursive))

    def tree(self):
        """
        Joins a recursive ls to a string
        """
        return self.display('.') + ('' if self.link is not None else '\n' + '\n'.join(self.ls_iter(recursive = True)))

    def name(self):
        """
        Gets the name of the context from its parent context.
        This is a heavy operation.
        """
        if len(self.parent_stack) == 0:
            return ''
        for name, value in getattr(self.parent_stack[0], 'children', {}).iteritems():
            if value is self:
                return name
        return "<not found in parent's children>"

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __str__(self):
        return '%s(%r%s)' % (self.__class__.__name__, getattr(self, 'value', self.link),
                             ''.join(map(', %s = %r'.__mod__,
                                         sorted((name, value) for (name, value) in
                                                getattr(self, 'children', {}).iteritems()
                                                if name != '.'))))

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __repr__(self):
        try:
            return '%s(%s/%s)' % (self.__class__.__name__,
                                  '/'.join(parent.name() for parent in reversed(self.parent_stack)),
                                  self.name())
        except AttributeError:
            # If someone illegally played with the parent_stack, we still want to
            # be able to do str()
            return super(Context, self).__str__()

