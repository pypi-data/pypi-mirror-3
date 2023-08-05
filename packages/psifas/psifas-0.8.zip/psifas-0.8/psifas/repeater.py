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

from datatypes.dummy import MetaSequence, MetaBytes, optimized_tuple, sequence_sum
from datatypes.sparse import SparseSequence, SparseString, maxint
from datatypes.abstract import NumberAbstraction, Top, SequenceAbstraction, StringAbstraction, CharAbstraction
from base import This, Segment, UniqueField, Psifas, Field, PayloadlessPlaceHolder, CLink
from arithmetic import Call, Equal, UBInt
from utils import pairwise
from constraint import SetSubValueConstraint, SetValueConstraint, Constraint, SetValueByValueConstraint
from payload_constraint import SetPayloadOffsetConstraint, SetPayloadConstraint
from multifield import Spiritualize
import numbers

class BasicSequence(Psifas):
    class SetItemConstraint(Constraint):
        def _run(self, location, index):
            item = location.context(str(index)).get_value()
            location.context().set_value(SparseSequence(optimized_tuple((Top,)) * index + optimized_tuple((item,)),
                                                        min_length = index + 1))

    class GetItemsConstraint(Constraint):
        def _run(self, location):
            sequence = location.context().get_value()
            if isinstance(sequence, MetaSequence):
                min_length = len(sequence)
            elif isinstance(sequence, SparseSequence):
                min_length = sequence.min_length
            else:
                # not a sequence?
                return
            # FEATURE: make more efficient by scanning only the sectors?
            for index, item in enumerate(sequence[:min_length]):
                location.context(str(index)).set_value(item)

    def _register_private_constraints(self, location):
        super(BasicSequence, self)._register_private_constraints(location)
        location.engine().constraints |= (self.GetItemsConstraint(location),
                                          SetValueConstraint(location, SparseSequence()))

class SequenceOf(BasicSequence):
    def __init__(self, *sub_psifases):
        super(SequenceOf, self).__init__(*(Field(str(index), sub_psifas) for index, sub_psifas in enumerate(sub_psifases)))
        
    def _register_private_constraints(self, location):
        super(SequenceOf, self)._register_private_constraints(location)
        location.engine().constraints.add(SetValueConstraint(location, SparseSequence.from_length(len(self._fields))))
        location.engine().constraints |= (self.SetItemConstraint(location, index) for index in xrange(len(self._fields)))

class FixedRepeater(BasicSequence):
    def __init__(self, counter, sub_psifas):
        super(FixedRepeater, self).__init__(*(Field(str(index), sub_psifas) for index in xrange(counter)))

    def _register_private_constraints(self, location):
        super(FixedRepeater, self)._register_private_constraints(location)
        location.engine().constraints.add(SetValueConstraint(location, SparseSequence.from_length(len(self._fields))))
        location.engine().constraints |= (self.SetItemConstraint(location, index) for index in xrange(len(self._fields)))

class _Repeater(BasicSequence):
    def __init__(self, sub_psifas_generator):
        super(_Repeater, self).__init__()
        self.sub_psifas_generator = sub_psifas_generator

    class AddItemsConstraints(Constraint):
        """
        a constraint for adding the repeaters constraints once we know they exist
        """
        def __init__(self, repeater_psifas, location):
            super(_Repeater.AddItemsConstraints, self).__init__(repeater_psifas, location)
            # at any given time, we know there're at least self.limit objects in the sequence
            self.limit = 0
            self.found_last = False
            
        def _run(self, repeater_psifas, location):
            sequence = location.context().get_value()
            if isinstance(sequence, MetaSequence):
                repeater_psifas.expand_limit(self, location, len(sequence), True)
            elif isinstance(sequence, SparseSequence):
                repeater_psifas.expand_limit(self, location, sequence.min_length,
                                             sequence.min_length == sequence.max_length)
                
    def expand_limit(self, add_items_constraint, location, new_limit, is_last_expansion):
        if new_limit > add_items_constraint.limit:
            self._expand_limit(location, add_items_constraint.limit, new_limit)
            add_items_constraint.limit = new_limit
        if is_last_expansion and not add_items_constraint.found_last:
            super(_Repeater, self)._register_last_child_payload_constraints(location, location[-1])
            add_items_constraint.found_last = True
            
    def _expand_limit(self, location, last_limit, new_limit):
        location.add_sublocations(self,
                                  list(Field(str(index), self.sub_psifas_generator.generate_sub_psifas(location, index)) for index in xrange(last_limit, new_limit)))
        if last_limit == 0:
            location.engine().constraints.add(SetPayloadOffsetConstraint(location[0], 0))
            
        for sub_location in location[last_limit:]:
            location.engine().constraints.add(SetPayloadOffsetConstraint(sub_location, NumberAbstraction))
            
            self._register_child_payload_constraints(location, sub_location)
            
        for sub_location, next_sub_location in pairwise(location[max(0, last_limit - 1):]):
            self._register_following_payloads_constraints(sub_location, next_sub_location)
            
        location.engine().constraints |= (self.SetItemConstraint(location, index)
                                          for index in xrange(last_limit, new_limit))
        
    def _register_private_constraints(self, location):
        super(_Repeater, self)._register_private_constraints(location)
        location.engine().constraints.add(self.AddItemsConstraints(self, location))

    _register_last_child_payload_constraints = BasicSequence._register_child_payload_constraints

class EmptyRepeater(_Repeater):
    def __init__(self):
        super(EmptyRepeater, self).__init__(self)
        
    def generate_sub_psifas(self, location, index):
        return PayloadlessPlaceHolder()

    def _register_private_constraints(self, location):
        super(EmptyRepeater, self)._register_private_constraints(location)
        location.engine().constraints.add(SetPayloadConstraint(location, ''))
    

class PayloadMap(Psifas):
    def __init__(self, sub_psifas_class, inner):
        super(PayloadMap, self).__init__(UniqueField('.map_inner', inner),
                                         UniqueField('.map_inner', EmptyRepeater()),
                                         UniqueField('.$map', _Repeater(self))
                                         )
        self.sub_psifas_class = sub_psifas_class

    class SetSequenceLengthBySequenceLength(Constraint):
        def _run(self, target_location, source_location):
            sequence = source_location.context().get_value()
            if isinstance(sequence, MetaSequence):
                target_location.context().set_value(SparseSequence.from_length(len(sequence)))
            elif isinstance(sequence, SparseSequence):
                target_location.context().set_value(SparseSequence(min_length = sequence.min_length, max_length = sequence.max_length))

    def generate_sub_psifas(self, location, index):
        return self.sub_psifas_class(CLink('../%s/%d' % (self._fields[0].name(self, location.parent), index)))

    def _register_private_constraints(self, location):
        super(PayloadMap, self)._register_private_constraints(location)
        location.engine().constraints |= (self.SetSequenceLengthBySequenceLength(location[0], location[2]),
                                          self.SetSequenceLengthBySequenceLength(location[2], location[0]))

class Map(PayloadMap):
    """
    Assumes that the mapping itself does not require any payload (like Operator1).
    """
    def _register_private_constraints(self, location):
        super(Map, self)._register_private_constraints(location)
        location.engine().constraints.add(SetPayloadConstraint(location[2], ''))
    

class PayloadReduce(Psifas):
    def __init__(self, sub_psifas_class, inner):
        super(PayloadReduce, self).__init__(UniqueField('.reduce_inner', inner),
                                            UniqueField('.reduce_inner', EmptyRepeater()),
                                            UniqueField('.reduce', _Repeater(self)))
        self.sub_psifas_class = sub_psifas_class

    class SetValueByLastElement(Constraint):
        def _run(self, target_location, source_location):
            sequence = source_location.context().get_value()
            if not isinstance(sequence, MetaSequence):
                return
            target_location.context().set_value(sequence[-1])

    class SetLastElementByValue(Constraint):
        def _run(self, target_location, source_location):
            sequence = target_location.context().get_value()
            if isinstance(sequence, MetaSequence):
                sequence_length = len(sequence)
            elif isinstance(sequence, SparseSequence) and sequence.min_length == sequence.max_length:
                sequence_length = sequence.min_length
            else:
                return
            target_location.context().set_value(SparseSequence.from_length(sequence_length - 1) + optimized_tuple((source_location.context().get_value(),)))

    def generate_sub_psifas(self, location, index):
        if index == 0:
            return CLink('../%s/0' % (self._fields[0].name(self, location.parent),))
        return self.sub_psifas_class(CLink('../../%s/%d' % (self._fields[2].name(self, location.parent), index - 1)),
                                     CLink('../../%s/%d' % (self._fields[0].name(self, location.parent), index)))
                                     
    def _register_private_constraints(self, location):
        super(PayloadReduce, self)._register_private_constraints(location)
        location.engine().constraints |= (PayloadMap.SetSequenceLengthBySequenceLength(location[0], location[2]),
                                          PayloadMap.SetSequenceLengthBySequenceLength(location[2], location[0]),
                                          self.SetValueByLastElement(location, location[2]),
                                          self.SetLastElementByValue(location[2], location))

class Reduce(PayloadReduce):
    def _register_private_constraints(self, location):
        super(Reduce, self)._register_private_constraints(location)
        location.engine().constraints.add(SetPayloadConstraint(location[2], ''))

class Repeater(Psifas):
    r"""
    Fixed Repeater example:

        >>> MY_REPEATER = Repeater(5, UBInt(2))
        >>> list(MY_REPEATER.parse('\x00\x01\x00\x02\x00\x03\x00\x04\x00\x00'))
        [1, 2, 3, 4, 0]
        >>> MY_REPEATER.build([4, 8, 7, 6, 5])
        '\x00\x04\x00\x08\x00\x07\x00\x06\x00\x05'

    Length-Value Repeater:

        >>> MY_REPEATER = Repeater(UBInt(2), Byte())
        >>> list(MY_REPEATER.parse('\x00\x03xxx'))
        ['x', 'x', 'x']
        >>> MY_REPEATER.build(['a', 'b', 'c', 'd'])
        '\x00\x04abcd'
    """
    class SetCounterByLengthConstraint(Constraint):
        def _run(self, target_location, source_location):
            sequence = source_location.context().get_value()
            if isinstance(sequence, MetaSequence):
                target_location.context().set_value(len(sequence))
            elif isinstance(sequence, SparseSequence) and sequence.min_length == sequence.max_length:
                target_location.context().set_value(sequence.min_length)

    class SetLengthByCounterConstraint(Constraint):
        def _run(self, target_location, source_location):
            counter = source_location.context().get_value()
            if not isinstance(counter, numbers.Number):
                return
            target_location.context().set_value(SparseSequence.from_length(counter))
            
    def __init__(self, counter, sub_psifas):
        super(Repeater, self).__init__(Field('.counter', counter),
                                       UniqueField('.$repeater', _Repeater(self)))
        self.sub_psifas = sub_psifas

    def generate_sub_psifas(self, location, index):
        return self.sub_psifas

    def _more_sub_psifases(self):
        return self.sub_psifas,
    
    def _register_private_constraints(self, location):
        super(Repeater, self)._register_private_constraints(location)
        location.engine().constraints |= (SetValueConstraint(location[0], NumberAbstraction),
                                          self.SetCounterByLengthConstraint(location[0], location[1]),
                                          self.SetLengthByCounterConstraint(location[1], location[0]))

class RepeatUntilTerm(_Repeater):
    r"""
    Use a psifas term to stop the repeats:

        >>> MY_REPEATER = Struct('seq', RepeatUntilTerm(UBInt(2), This > 7),
        ...                      'leftover', Leftover())
        >>> parsed_container = MY_REPEATER.parse('\x00\x01\x00\x02\x00\x09\x00\x01')
        >>> parsed_container
        Container(...)
        >>> list(parsed_container.seq)
        [1, 2, 9]

        >>> MY_REPEATER.build(Container(seq = [0, 1, 8], leftover = ''))
        '\x00\x00\x00\x01\x00\x08'
    """
    
    def __init__(self, sub_psifas, stop_psifas, stop_repeat_field_name = '.stop_repeat', min_length = 1):
        if sub_psifas.spiritual is not True:
            sub_psifas = Spiritualize(sub_psifas)
        
        super(RepeatUntilTerm, self).__init__(self)

        self.sub_psifas = Psifas(Field('.$repeater', sub_psifas),
                                 Field(stop_repeat_field_name, stop_psifas),
                                 spiritual = True)
        
        self.stop_repeat_field_name = stop_repeat_field_name
        self.min_length = 1

    class SetLengthByStopConditionConstraint(Constraint):
        def _run(self, repeater_psifas, location, index):
            is_stop = location.context('%s/%s' % (index, repeater_psifas.stop_repeat_field_name)).get_value()
            if is_stop is True:
                location.context().set_value(SparseSequence.from_length(index + 1))
            elif is_stop is False:
                location.context().set_value(SparseSequence(min_length = index + 2))

    class SetStopConditionByLengthConstraint(Constraint):
        def _run(self, repeater_psifas, location):
            sequence = location.context().get_value()
            if isinstance(sequence, MetaSequence):
                length = len(sequence)
            elif isinstance(sequence, SparseSequence) and sequence.min_length == sequence.max_length:
                length = sequence.min_length
            else:
                return
            location.context('%s/%s' % (length - 1, repeater_psifas.stop_repeat_field_name)).set_value(True)

    def generate_sub_psifas(self, location, index):
        return self.sub_psifas

    def _more_sub_psifases(self):
        return self.sub_psifas,

    def _expand_limit(self, location, last_limit, new_limit):
        # set "False" in all the tests, except for the last one
        super(RepeatUntilTerm, self)._expand_limit(location, last_limit, new_limit)
        for sub_location in location[max(0, last_limit - 1):new_limit - 1]:
            location.engine().constraints.add(SetSubValueConstraint(sub_location,
                                                                    self.stop_repeat_field_name,
                                                                    False))
        location.engine().constraints.add(self.SetLengthByStopConditionConstraint(self, location, new_limit - 1))

    def _register_private_constraints(self, location):
        super(RepeatUntilTerm, self)._register_private_constraints(location)
        location.engine().constraints |= (SetValueConstraint(location, SparseSequence(min_length = self.min_length)),
                                          self.SetStopConditionByLengthConstraint(self, location))
        
class RepeatUntil(Psifas):
    r"""
    Repeat until some value.

        >>> MY_REPEATER = RepeatUntil(UBInt(2), 0xFFFF)
        >>> list(MY_REPEATER.parse('\x00\x01\x00\x02\xFF\xFF'))
        [1, 2, 65535]

    You don't have to include that last element:

        >>> MY_REPEATER = RepeatUntil(UBInt(2), 0xFFFF, including = False)
        >>> list(MY_REPEATER.parse('\x00\x01\x00\x02\xFF\xFF'))
        [1, 2]
        >>> MY_REPEATER.build([3,2,1,0])
        '\x00\x03\x00\x02\x00\x01\x00\x00\xff\xff'
    """
    class ChopLastConstraint(SetValueByValueConstraint):
        def _wrap(self, value):
            if isinstance(value, MetaSequence) or isinstance(value, SparseSequence):
                # works for sparse sequences too:
                return value[:-1]
            return SparseSequence()
        
    class AddLastConstraint(SetValueByValueConstraint):
        def _wrap(self, value, last_element):
            if isinstance(value, MetaSequence):
                return sequence_sum(value, [last_element])
            elif isinstance(value, SparseSequence):
                return value + [last_element]
            return SparseSequence()
    
    class RepeatUntilConstraint(Constraint):
        def _run(self, repeat_until_psifas, location):
            if not location[1].context().get_is_concrete():
                return
            is_including = location[1].context().get_value()
            if is_including:
                location.engine().constraints |= (SetValueByValueConstraint(location, location[2]),
                                                  SetValueByValueConstraint(location[2], location))
            
            else:
                if not location[0].context().get_is_concrete():
                    return
                last_element = location[0].context().get_value()
                location.engine().constraints |= (repeat_until_psifas.ChopLastConstraint(location, location[2]),
                                                  repeat_until_psifas.AddLastConstraint(location[2], location, last_element))
                
    def __init__(self, sub_psifas, last_element, including = True):
        super(RepeatUntil, self).__init__(Field('.last_element', last_element),
                                          UniqueField('.including', including),
                                          UniqueField('.until_term', RepeatUntilTerm(sub_psifas, Equal(This, This/'../../.last_element'))))
        
    def _register_private_constraints(self, location):
        super(RepeatUntil, self)._register_private_constraints(location)
        location.engine().constraints.add(self.RepeatUntilConstraint(self, location))

                

class PascalString(Segment):
    r"""
    Nice version which is equivalent to Segment(UBInt(1)).

    >>> my_pascal_string = PascalString()
    >>> my_pascal_string.parse('\x03abc')
    'abc'
    >>> my_pascal_string.build('ABCD')
    '\x04ABCD'
    """
    def __new__(cls, *args, **kws):
        # don't use the Segment's __new__
        return Psifas.__new__(cls)

    def __init__(self, sizer_size = 1, sizer_format = UBInt):
        super(PascalString, self).__init__(sizer_format(Segment(sizer_size)))


class Slice(Psifas):
    r"""
    Takes a slice from a sequence or a string.

        >>> MY_STRUCT = Struct('slice_separator', UBInt(1),
        ...                    'joined_segment', Payload(),
        ...                    'first_slice', This.joined_segment[:This.slice_separator],
        ...                    'second_slice', This.joined_segment[This.slice_separator:]
        ...                    )
        >>> parsed_container = MY_STRUCT.parse('\x030123456789')
        >>> parsed_container
        Container(...)
        >>> parsed_container.first_slice
        '012'
        >>> parsed_container.second_slice
        '3456789'
        >>> MY_STRUCT.build(Container(slice_separator = 6,
        ...                           first_slice = 'AAAAAA',
        ...                           second_slice = 'BB'))
        '\x06AAAAAABB'


        >>> MY_STRUCT = Struct('some_payload', Payload(),
        ...                    'almost_all', This.some_payload[:-1],
        ...                    'last', This.some_payload[-1])
        >>> MY_STRUCT.build(Container(almost_all = 'abc', last = 'd'))
        'abcd'
    """
    
    def __init__(self, source, key):
        if isinstance(key, slice) and (isinstance(key.start, Psifas) or isinstance(key.stop, Psifas) or isinstance(key.step, Psifas)):
            key = Call(slice, key.start, key.stop, key.step)
        super(Slice, self).__init__(UniqueField('.slice_source', source),
                                    UniqueField('.slice_key', key))
        
    class GetSliceConstraint(Constraint):
        def _run(self, target_location, sequence_location, key_location):
            if not key_location.context().get_is_concrete():
                return
            key = key_location.context().get_value()
            if not isinstance(key, (numbers.Number, slice)):
                return
            
            sequence = sequence_location.context().get_value()
            if not isinstance(sequence, (StringAbstraction, SequenceAbstraction)):
                return
            target_location.context().set_value(sequence[key])

    class SetSliceConstraint(Constraint):
        def _run(self, target_location, sequence_location, key_location):
            if not key_location.context().get_is_concrete():
                return
            key = key_location.context().get_value()
            if isinstance(key, numbers.Number):
                self._run_index(target_location, sequence_location, key)
            elif isinstance(key, slice):
                self._run_slice(target_location, sequence_location, key)

        def _run_index(self, target_location, item_location, key):
            item = item_location.context().get_value()

            target_sequence = target_location.context().get_value()

            if isinstance(target_sequence, StringAbstraction):
                min_length, max_length = StringAbstraction.length_range(target_sequence)
                result_class = SparseString
            elif isinstance(target_sequence, SequenceAbstraction):
                min_length, max_length = SequenceAbstraction.length_range(target_sequence)
                result_class = SparseSequence
            elif (item is not Top) and (item is not CharAbstraction) and (not isinstance(item, MetaBytes) or len(item) != 1):
                # if item is not a char, result_class must be SparseSequence
                result_class = SparseSequence
                min_length = 0
                max_length = maxint
            else:
                return
            
            if key < 0:
                if min_length != max_length:
                    # cannot know where the index is
                    return
                key = max_length + key
                if key < 0:
                    # too small?
                    return
            new_target_sequence = result_class.from_length(key) + result_class([item], min_length = 1)
            target_location.context().set_value(new_target_sequence)

        def _get_target_length(self, target_location):
            target_sequence = target_location.context().get_value()
            if isinstance(target_sequence, StringAbstraction):
                target_min_length, target_max_length = StringAbstraction.length_range(target_sequence)
            elif isinstance(target_sequence, SequenceAbstraction):
                target_min_length, target_max_length = SequenceAbstraction.length_range(target_sequence)
            else:
                return None
            if target_min_length != target_max_length:
                return None
            return target_min_length

        def _run_slice(self, target_location, sequence_location, key):
            step = key.step
            if step is None:
                step = 1
            start = key.start
            if start is None:
                if step > 0:
                    start = 0
                else:
                    start = -1
            stop = key.stop
            
            sequence = sequence_location.context().get_value()
            
            if isinstance(sequence, StringAbstraction):
                sequence_min_length, sequence_max_length = StringAbstraction.length_range(sequence)
                result_class = SparseString
            elif isinstance(sequence, SequenceAbstraction):
                sequence_min_length, sequence_max_length = SequenceAbstraction.length_range(sequence)
                result_class = SparseSequence
            else:
                return
            if isinstance(sequence, (SparseString, SparseSequence)):
                sequence = sequence.value

            # start is not None:
            if start < 0:
                target_length = self._get_target_length(target_location)
                if target_length is None:
                    return
                start = target_length + start
                if start < 0:
                    return
            # start >= 0
            if step < 0:
                result = [result_class.default_element] * (start + 1)
                result[start:start + (step * len(sequence)):step] = sequence
                if len(result) != start + 1:
                    return
                target_location.context().set_value(result_class(result, min_length = start + 1))
            else: # step > 0
                suffix = [result_class.default_element] * (step * len(sequence))
                suffix[0:(step * len(sequence)):step] = sequence
                if len(suffix) != step * len(sequence):
                    return
                length_kws = {}
                if stop is None:
                    # There are no more items
                    length_kws.update(min_length = (step * (sequence_min_length - 1)) + 1,
                                      max_length = (step * sequence_max_length))
                else:
                    if stop < 0:
                        length_kws.update(min_length = (step * (sequence_min_length - 1)) + 1 - stop,
                                          max_length = (step * sequence_max_length) - stop)
                    else:
                        length_kws.update(min_length = (step * (sequence_min_length - 1) + 1))
                            
                target_location.context().set_value(result_class.from_length(start) + result_class(suffix, **length_kws))

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          self.GetSliceConstraint(location, location[0], location[1]),
                                          self.SetSliceConstraint(location[0], location, location[1]))

Psifas.__getitem__ = lambda self, key: Slice(self, key)

