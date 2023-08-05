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

from datatypes.pretty import Pretty
from datatypes.ordered_set import OrderedSet

# DEBUG
# import time

class Constraint(Pretty):
    @classmethod
    def create(cls, *parameters):
        # create without registering
        self = super(Constraint, cls).__new__(cls)
        self._init(*parameters)
        return self

    def __init__(self, *parameters):
        super(Constraint, self).__init__()
        self._init(*parameters)        

    def _init(self, *parameters):
        # required for the deepcopy:
        self.parameters = parameters
        self.dependencies = OrderedSet()
        # constraint queue
        self.constraint_queue = None
        self.constraint_queue_index = None
        
        # DEBUG
        self.runs = 0
        # self.tottime = 0
        
    def _run(self, *parameters):
        """
        override this when the constraint can handle abstract dependencies
        """
        for context in self.dependencies:
            if not context.get_is_concrete():
                return
        self._run_concrete(*parameters)

    def _run_concrete(self, *parameters):
        pass

    def run(self):
        self.runs += 1
        # start_time = time.time()
        # print 'running %s %s' % (self.__class__.__name__, ', '.join(str(param) for param in self.parameters))
        return self._run(*self.parameters)
    # self.tottime += time.time() - start_time

class BoundConstraint(Constraint):
    def _run(self, parent_constraint, func_name):
        return getattr(parent_constraint, func_name)(*parent_constraint.parameters)

class ExternalConstraint(Constraint):
    def _run(self, external_object, function_name, *parameters):
        return getattr(external_object, function_name)(*parameters)

class SingleExecutionConstraint(Constraint):
    def __init__(self, *parameters):
        super(SingleExecutionConstraint, self).__init__(*parameters)
        self.executed = False
        
    def run(self):
        if self.executed:
            return
        self.executed = super(SingleExecutionConstraint, self).run()
            

class SetValueConstraint(Constraint):
    def _run(self, location, value):
        location.context().set_value(value)

class SetSubValueConstraint(Constraint):
    def _run(self, location, path, value):
        location.context(path).set_value(value)

class SetLinkConstraint(Constraint):
    def _run(self, location, value):
        if not location.direct_context().set_link(value):
            location.engine().postponed_constraints.add(self)
        
class SetContextLinkConstraint(Constraint):
    def _run(self, context, link):
        while context.replacer is not None:
            context = context.replacer
        if context.set_link(link):
            return
        context.engine.postponed_constraints.add(self)

class SetValueByFieldConstraint(Constraint):
    def _run(self, location, field_name):
        location.context().set_value(location.context(field_name).get_value())


class SetFieldByValueConstraint(Constraint):
    def _run(self, location, field_name):
        location.context(field_name).set_value(location.context().get_value())

class SetValueByValueConstraint(Constraint):
    def _wrap(self, value):
        """
        This function will be called on the source-value before passing to the target value.
        Override it when you need.
        """
        return value
        
    def _run(self, target_location, source_location, *args):
        target_location.context().set_value(self._wrap(source_location.context().get_value(), *args))
