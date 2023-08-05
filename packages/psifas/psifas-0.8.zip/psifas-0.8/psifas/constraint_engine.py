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

from datatypes.deque import deque
from datatypes.ordered_set import OrderedSet
from datatypes.dummy import sortedset
from location import Location
from context import Context
from constraint import Constraint, SetValueConstraint
import operator
from copy import deepcopy
from itertools import chain

class ConstraintQueue(object):
    def __init__(self):
        super(ConstraintQueue, self).__init__()
        self.queue = deque()
        self.index_limit = 0
        self.garbage = 0

    def _add_normal(self, constraint):
        if constraint.constraint_queue is self:
            # already in
            return
        else:
            assert constraint.constraint_queue is None
        self.queue.append(constraint)
        constraint.constraint_queue = self
        constraint.constraint_queue_index = self.index_limit + len(self.queue)

    def _add_head(self, constraint):
        if constraint.constraint_queue is self:
            # creating a new instance in the head, but leaving the old instance in its place.
            self.garbage += 1 
        else:
            assert constraint.constraint_queue is None
            
        # we will reinsert the constraint if its already in.
        # the other places will have wrong indexes.
        
        self.queue.appendleft(constraint)
        self.index_limit -= 1
        
        constraint.constraint_queue = self
        constraint.constraint_queue_index = self.index_limit + 1

    def clean_garbage(self):
        for cycle in xrange(len(self)):
            constraint = self.pop()
            self._add_normal(constraint)

    def add(self, constraint):
        """
        When adding a new constraint - if all of its dependencies are concrete, it will be added at the head
        to be evaluated as soon as possible (if it's already inside, it will be moved to the head).
        Otherwise, if it is not already inside, it will be added last.
        """
        if not isinstance(constraint, Constraint):
            raise TypeError("Not a Constraint", constraint)
        if all(context.is_concrete for context in constraint.dependencies):
            return self._add_head(constraint)
        else:
            return self._add_normal(constraint)
        
    def pop(self):
        constraint = self.queue.popleft()
        self.index_limit += 1
        while constraint.constraint_queue_index != self.index_limit:
            self.garbage -= 1
            constraint = self.queue.popleft()
            self.index_limit += 1
        
        constraint.constraint_queue = None
        constraint.constraint_queue_index = None
        return constraint

    def pop_all(self):
        while len(self) > 0:
            yield self.pop()

    def discard(self, constraint):
        if constraint.constraint_queue is not self:
            assert constraint.constraint_queue is None
            return
        
        constraint.constraint_queue = None
        constraint.constraint_queue_index = None
            
    def __contains__(self, constraint):
        return getattr(constraint, 'constraint_queue', None) is self

    def __len__(self):
        return len(self.queue) - self.garbage

    def __ior__(self, iterable):
        for constraint in iterable:
            self.add(constraint)
        return self

class ConstraintEngineRevert(object):
    def __init__(self, engine, exception_class, exception_constraint, exception_location):
        super(ConstraintEngineRevert, self).__init__()
        # Doesn't duplicate the engine instance.
        # This way we can update engine.__dict__ back to its original value, and all the copied
        # objects (like sub-locations) will still have references to the original engine instance
        self.engine_dict, self.exception_constraint, self.exception_location = deepcopy((engine.__dict__,
                                                                                         exception_constraint,
                                                                                         exception_location),
                                                                                        memo = {id(engine): engine})
        self.exception_class = exception_class
        
class ConstraintEngine(object):
    def __init__(self):
        super(ConstraintEngine, self).__init__()
        self.constraints = ConstraintQueue() # sortedset(key = default_key_function)
        self.all_constraints = OrderedSet()
        self.postponed_constraints = OrderedSet()
        self.location = Location(None, '.', None)
        self.location._context = Context()
        self.location.context().engine = self
        self.change_count = 0
        self.running_constraint = None
        # Used by the Try Psifas
        self.exception_classes = ()
        self.revert_points = deque()

    def add_revert_constraints(self, constraints_creator_func):
        for revert_point in self.revert_points:
            revert_point.engine_dict['constraints'] |= constraints_creator_func(revert_point.engine_dict)
        self.constraints |= constraints_creator_func(self.__dict__)

    def reset_constraints(self):
        for constraint in chain(self.all_constraints, self.postponed_constraints):
            constraint.runs = 0
            constraint.tottime = 0
        for revert_point in self.revert_points:
            for constraint in chain(revert_point.engine_dict['all_constraints'],
                                    revert_point.engine_dict['postponed_constraints']):
                constraint.runs = 0
                # constraint.tottime = 0
                
                
    def run_constraint(self, constraint):
        self.running_constraint = constraint
        self.all_constraints.add(constraint)
        try:
            constraint.run()
        except self.exception_classes, e:
            for revert_point in self.revert_points:
                if not isinstance(e, revert_point.exception_class):
                    continue
                self.__dict__.update(revert_point.engine_dict)
                if revert_point.exception_location is not None:
                    self.constraints.add(SetValueConstraint(revert_point.exception_location, e))
                if revert_point.exception_constraint is not None:
                    self.constraints.add(revert_point.exception_constraint)
                # reinsert the postponed constraints
                self.constraints |= self.postponed_constraints
                self.postponed_constraints.clear()
                break
            else:
                raise
    

    def run(self):
        self.constraints |= self.postponed_constraints
        self.postponed_constraints.clear()
        while True:
            while len(self.constraints) > 0:
                self.run_constraint(self.constraints.pop())
                    
            # run again all constraints
            change_count = self.change_count

            for index, constraint in enumerate(self.all_constraints):
                # We must notice that constraints that keep running with abstract values and, for example, add other constraints,
                # may cause infinite loop by readding these constraints over and over.
                if all(context.is_concrete for context in constraint.dependencies):
                    continue
                # DEBUG:
                # if index == ???:
                #     import pdb; pdb.set_trace()
                self.run_constraint(constraint)
                # DEBUG:
                # if change_count != self.change_count or len(self.constraints) != 0:
                #     print 'index', index
                #     import pdb; pdb.set_trace()
                if len(self.constraints) != 0:
                    break
            else:
                if change_count == self.change_count:
                    # No constraint made a change - break
                    break

