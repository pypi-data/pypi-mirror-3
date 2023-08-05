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

from constraint import Constraint, BoundConstraint
from datatypes.sparse import SparseString
from datatypes.abstract import StringAbstraction

import numbers


class SetPayloadOffsetConstraint(Constraint):
    def _run(self, location, value):
        location.payload_offset_context().set_value(value)

class SetPayloadConstraint(Constraint):
    def _run(self, location, value):
        location.payload_context().set_value(value)

class SetPayloadLinkConstraint(Constraint):
    def _run(self, location, link):
        location.direct_payload_context().set_value(link)

class SetPayloadByParentPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetPayloadByParentPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
        
    def _run(self, location, sub_location):
        if not sub_location.payload_offset_context().get_is_concrete():
            return
        self.sub_payload_offset = sub_location.payload_offset_context().get_value()
        if not isinstance(self.sub_payload_offset, numbers.Number):
            return
        location.context().engine.constraints.add(self.step2_constraint)

    def step2(self, location, sub_location):
        parent_payload = location.payload_context().get_value()
        if not isinstance(parent_payload, StringAbstraction):
            return
        sub_location.payload_context().set_value(SparseString.prefix(parent_payload[self.sub_payload_offset:]))

class SetLastPayloadByParentPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetLastPayloadByParentPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
        
    # for the last sub_location
    def _run(self, location, sub_location):
        if not sub_location.payload_offset_context().get_is_concrete():
            return
        self.sub_payload_offset = sub_location.payload_offset_context().get_value()
        if not isinstance(self.sub_payload_offset, numbers.Number):
            return
        location.context().engine.constraints.add(self.step2_constraint)

    def step2(self, location, sub_location):
        parent_payload = location.payload_context().get_value()
        if not isinstance(parent_payload, StringAbstraction):
            return
        sub_location.payload_context().set_value(parent_payload[self.sub_payload_offset:])

class SetLastPayloadOffsetByParentPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetLastPayloadOffsetByParentPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
        self.step1_done = False
        
    # for the last sub_location
    def _run(self, location, sub_location):
        if self.step1_done:
            return
        sub_payload = sub_location.payload_context().get_value()
        if not isinstance(sub_payload, StringAbstraction):
            return
        min_length, max_length = StringAbstraction.length_range(sub_payload)
        if min_length != max_length:
            return
        self.payload_length = min_length
        location.context().engine.constraints.add(self.step2_constraint)
        self.step1_done = True

    def step2(self, location, sub_location):
        parent_payload = location.payload_context().get_value()
        if not isinstance(parent_payload, StringAbstraction):
            return
        min_length, max_length = StringAbstraction.length_range(parent_payload)
        if min_length != max_length:
            return
        if min_length < self.payload_length:
            return
        sub_location.payload_offset_context().set_value(min_length - self.payload_length)

class SetParentPayloadByPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetParentPayloadByPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
        
    def _run(self, location, sub_location):
        if not sub_location.payload_offset_context().get_is_concrete():
            return
        self.sub_payload_offset = sub_location.payload_offset_context().get_value()
        if not isinstance(self.sub_payload_offset, numbers.Number):
            return
        location.context().engine.constraints.add(self.step2_constraint)

    def step2(self, location, sub_location):
        sub_payload = sub_location.payload_context().get_value()
        if isinstance(sub_payload, StringAbstraction):
            location.payload_context().set_value(SparseString.from_length(self.sub_payload_offset) + sub_payload + SparseString())
        else:
            location.payload_context().set_value(SparseString(min_length = self.sub_payload_offset))
            
class SetParentPayloadByLastPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetParentPayloadByLastPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
        
    def _run(self, location, sub_location):
        if not sub_location.payload_offset_context().get_is_concrete():
            return
        self.sub_payload_offset = sub_location.payload_offset_context().get_value()
        if not isinstance(self.sub_payload_offset, numbers.Number):
            return
        location.context().engine.constraints.add(self.step2_constraint)

    def step2(self, location, sub_location):
        sub_payload = sub_location.payload_context().get_value()
        if isinstance(sub_payload, StringAbstraction):
            location.payload_context().set_value(SparseString.from_length(self.sub_payload_offset) + sub_payload)
        else:
            location.payload_context().set_value(SparseString(min_length = self.sub_payload_offset))
            
class SetPayloadOffsetByPreviousPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetPayloadOffsetByPreviousPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
    
    def _run(self, location, next_location):
        if not location.payload_offset_context().get_is_concrete():
            return
        self.payload_offset = location.payload_offset_context().get_value()
        if not isinstance(self.payload_offset, numbers.Number):
            return
        location.context().engine.constraints.add(self.step2_constraint)

    def step2(self, location, next_location):
        payload = location.payload_context().get_value()
        if not isinstance(payload, StringAbstraction):
            return
        min_length, max_length = StringAbstraction.length_range(payload)
        if min_length != max_length:
            return
        
        next_location.payload_offset_context().set_value(self.payload_offset + min_length)

class SetPreviousPayloadOffsetByPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetPreviousPayloadOffsetByPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
    
    def _run(self, location, next_location):
        if not next_location.payload_offset_context().get_is_concrete():
            return
        self.next_payload_offset = next_location.payload_offset_context().get_value()
        if not isinstance(self.next_payload_offset, numbers.Number):
            return
        location.context().engine.constraints.add(self.step2_constraint)

    def step2(self, location, next_location):
        payload = location.payload_context().get_value()
        if not isinstance(payload, StringAbstraction):
            return
        min_length, max_length = StringAbstraction.length_range(payload)
        if min_length != max_length:
            return
        location.payload_offset_context().set_value(self.next_payload_offset - min_length)

class SetPreviousPayloadSizeByPayloadConstraint(Constraint):
    def __init__(self, *parameters):
        super(SetPreviousPayloadSizeByPayloadConstraint, self).__init__(*parameters)
        self.step2_constraint = BoundConstraint(self, 'step2')
        
    def _run(self, location, next_location):
        if not next_location.payload_offset_context().get_is_concrete():
            return
        self.next_payload_offset = next_location.payload_offset_context().get_value()
        if not isinstance(self.next_payload_offset, numbers.Number):
            return
        location.context().engine.constraints.add(self.step2_constraint)

    def step2(self, location, next_location):
        if not location.payload_offset_context().get_is_concrete():
            return
        payload_offset = location.payload_offset_context().get_value()
        if not isinstance(payload_offset, numbers.Number):
            return
        location.payload_context().set_value(SparseString.from_length(self.next_payload_offset - payload_offset))


class SetPayloadByValueConstraint(Constraint):
    def _run(self, target_location, source_location):
        target_location.payload_context().set_value(source_location.context().get_value())

class SetValueByPayloadConstraint(Constraint):
    def _run(self, target_location, source_location):
        target_location.context().set_value(source_location.payload_context().get_value())
            
            
