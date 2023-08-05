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

from itertools import islice, chain
from copy import deepcopy
from utils import pairwise, Link, Path
from psifas_exceptions import DecipherException, PsifasException
from location import Location
from datatypes.dummy import DummyPayload, MetaBytes
from datatypes.abstract import NumberAbstraction, StringAbstraction, is_abstract, Top
from datatypes.pretty import Pretty
from datatypes.sparse import SparseString
from payload_constraint import (SetPayloadConstraint, SetPayloadOffsetConstraint, SetPayloadByParentPayloadConstraint, SetParentPayloadByPayloadConstraint,
                                SetPayloadOffsetByPreviousPayloadConstraint, SetPreviousPayloadOffsetByPayloadConstraint, SetPreviousPayloadSizeByPayloadConstraint,
                                SetLastPayloadByParentPayloadConstraint, SetLastPayloadOffsetByParentPayloadConstraint, SetParentPayloadByLastPayloadConstraint,
                                SetPayloadByValueConstraint, SetValueByPayloadConstraint)
from constraint_engine import ConstraintEngine, ConstraintEngineRevert
from constraint import (Constraint, SetValueConstraint, SetLinkConstraint, SingleExecutionConstraint,
                        SetFieldByValueConstraint, SetValueByFieldConstraint, SetValueByValueConstraint)
import multifield
import numbers

class Field(Pretty):
    __slots__ = ['_full_name', '_name', 'psifas']
    def __init__(self, full_name, psifas):
        super(Field, self).__init__()
        # assert '/' not in full_name
        # assert name not in ('', '.', '..', '...')
        if not isinstance(psifas, Psifas):
            psifas = Constant(psifas)
            
        self._full_name = full_name
        self._name = full_name.split('$', 1)[0]
        self.psifas = psifas

    def _pretty_attributes(self):
        return ('full_name', self._full_name), ('psifas', self.psifas)

    def is_nameless(self):
        return self._name in ('.', '')

    def name(self, creator, location):
        return self._name

    def full_name(self, creator, location):
        return self._full_name

    def create_sublocation(self, creator, parent_location, index):
        if self.psifas._prepared_engine is None:
            location = Location(index,
                                self.full_name(creator, parent_location),
                                parent_location)
            location._context = parent_location.context().get_child(self.name(creator, parent_location))
            self.psifas.register_constraints(location)
            return location
        # insert a copy of the engine's location instead of the current location
        # FEATURE: create _prepared_engines_queue instead of waisting time on deepcopy ?
        engine = deepcopy(self.psifas._prepared_engine)
        
        engine.location.index = index
        engine.location.full_name = self.full_name(creator, parent_location)
        engine.location.parent = parent_location

        target_context = parent_location.direct_context().get_child(self.name(creator, parent_location))

        # FEATURE: set the used constraint in the move_into to something relevant, instead of just the last called constraint.
        engine.location.direct_context().move_into(target_context)
        engine.location.direct_context().replacer = target_context
        
        parent_location.engine().constraints |= engine.constraints.pop_all()
        # retry the posponed constraints:
        parent_location.engine().constraints |= engine.postponed_constraints
        parent_location.engine().all_constraints |= engine.all_constraints
            
        # parent_location[index] = engine.location
        return engine.location
        

class UniqueField(Field):
    def name(self, creator, location):
        if self._name != self._full_name:
            # there was a '$' in the name - the unique id part of the description
            return super(UniqueField, self).name(creator, location)
        return "%s#%s%d" % (self._name, creator.__class__.__name__, location.id)

    def full_name(self, creator, location):
        return "%s#%s%d" % (self._full_name, creator.__class__.__name__, location.id)

    def is_nameless(self):
        if self._name != self._full_name:
            return super(UniqueField, self).is_nameless()
        return False
    

class Psifas(Pretty):
    spiritual = False
    
    def __init__(self, *fields, **kw):
        self._fields = fields
        self.spiritual = kw.pop('spiritual', self.spiritual)
        self.last_engine = None
        self._prepared_engine = None
        self._prepared_height = None

        super(Psifas, self).__init__(**kw)

    def _pretty_attributes(self):
        return [(key, value) for (key, value) in super(Psifas, self)._pretty_attributes() if key not in ('last_engine', '_prepared_engine', '_prepared_height')]

    def __deepcopy__(self, memo):
        return self

    def create_engine(self, engine_class = ConstraintEngine):
        # When debugging, we can use the last_engine.
        if self._prepared_engine is None:
            engine = engine_class()
            self.register_constraints(engine.location)
        else:
            engine = deepcopy(self._prepared_engine)
        return engine

    def sub_psifases(self):
        return chain((field.psifas for field in self._fields),
                     self._more_sub_psifases())

    def _more_sub_psifases(self):
        return ()

    def prepare(self, min_height = 1):
        # my_psifas.prepare().parse(...) will make the preparation on the first execution.
        self._prepared_height = 0
        for sub_psifas in self.sub_psifases():
            sub_psifas.prepare(min_height)
            self._prepared_height = max(self._prepared_height,
                                        sub_psifas._prepared_height + 1)
        if self._prepared_height >= min_height:
            self._prepared_engine = self.create_engine()
            self._prepared_engine.run()
            self._prepared_engine.constraints.clean_garbage()
            # debug:
            self._prepared_engine.reset_constraints()
        else:
            self._prepared_engine = None
        return self 

    def _register_private_constraints(self, location):
        location.engine().constraints.add(SetPayloadConstraint(location, SparseString()))
    
    def _register_children_constraints(self, location):
        if len(self._fields) == 0:
            return
        
        location.engine().constraints.add(SetPayloadOffsetConstraint(location[0], 0))
        for sub_location in location[1:]:
            location.engine().constraints.add(SetPayloadOffsetConstraint(sub_location, NumberAbstraction))
        
        for sub_location, next_sub_location in islice(pairwise(location), len(self._fields)):
            # for the last sublocation we have better constraints in _register_last_child_payload_constraints:
            self._register_child_payload_constraints(location, sub_location)
            self._register_following_payloads_constraints(sub_location, next_sub_location)
            
        self._register_last_child_payload_constraints(location, location[-1])

    def _register_child_payload_constraints(self, location, sub_location):
        location.engine().constraints |= (SetPayloadByParentPayloadConstraint(location, sub_location),
                                          SetParentPayloadByPayloadConstraint(location, sub_location))

    def _register_following_payloads_constraints(self, sub_location, next_sub_location):
        sub_location.engine().constraints |= (SetPayloadOffsetByPreviousPayloadConstraint(sub_location, next_sub_location),
                                              SetPreviousPayloadOffsetByPayloadConstraint(sub_location, next_sub_location),
                                              SetPreviousPayloadSizeByPayloadConstraint(sub_location, next_sub_location))
        
    
    def _register_last_child_payload_constraints(self, location, last_sub_location):
        location.engine().constraints |= (SetLastPayloadByParentPayloadConstraint(location, last_sub_location),
                                          SetLastPayloadOffsetByParentPayloadConstraint(location, last_sub_location),
                                          SetParentPayloadByLastPayloadConstraint(location, last_sub_location))
        
    def register_constraints(self, location):
        location.context().set_spiritual(self.spiritual)
        location.create_sublocations(self, self._fields)
        self._register_children_constraints(location)
        self._register_private_constraints(location)
    
    def _fix_payload(self, payload, ignore_leftover):
        if not isinstance(payload, StringAbstraction):
            # it is a stream
            return SparseString(DummyPayload(payload))
        elif ignore_leftover:
            return SparseString(payload)
        return payload

    def complete(self, value):
        """
        builds the value, but returns the context's value.
        Usefull when only the auto-complete features are required.
        """
        engine = self.last_engine = self.create_engine()
        engine.add_revert_constraints(lambda engine_dict: (SetValueConstraint(engine_dict['location'], value),
                                                           SetPayloadOffsetConstraint(engine_dict['location'], None)))
        engine.run()
        if len(engine.postponed_constraints) > 0:
            raise DecipherException("some constraints were postponed (link reference above root?)")
        return engine.location.context().value
    
    def build(self, value, allow_sparse = False):
        engine = self.last_engine = self.create_engine()
        
        engine.add_revert_constraints(lambda engine_dict: (SetValueConstraint(engine_dict['location'], value),
                                                           SetPayloadOffsetConstraint(engine_dict['location'], None)))
        engine.run()
        if len(engine.postponed_constraints) > 0:
            raise DecipherException("some constraints were postponed (link reference above root?)")
        payload = engine.location.payload_context().value
        if not allow_sparse and is_abstract(payload):
            raise DecipherException("deciphering did not finish due to missing dependencies: \n%s" % (engine.location.context().tree(),))
        return payload

    def parse(self, payload, ignore_leftover = False):
        payload = self._fix_payload(payload, ignore_leftover)
        engine = self.last_engine = self.create_engine()
        engine.add_revert_constraints(lambda engine_dict: (SetPayloadConstraint(engine_dict['location'], payload),
                                                           SetPayloadOffsetConstraint(engine_dict['location'], None)))
        engine.run()
        if len(engine.postponed_constraints) > 0:
            raise DecipherException("some constraints were postponed (link reference above root?)")
        value = engine.location.context().value
        if value is Top:
            raise DecipherException("deciphering did not finish due to missing dependencies: \n%s" % (engine.location.context().tree(),))
        return value
        
    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __radd__(self, other):
        # If it was a psifas, the __add__ would have been called.
        return Constant(other) + self
    
    def on(self, *args, **kw):
        return On(self, *args, **kw)

    def struct(self):
        return multifield.Struct('.', self)

class PlaceHolder(Psifas):
    spiritual = None
    
    def __init__(self):
        super(PlaceHolder, self).__init__()

    def register_constraints(self, location):
        location.context().set_spiritual(self.spiritual)

class PayloadlessPlaceHolder(Psifas):
    spiritual = None
    
    def __init__(self):
        super(PayloadlessPlaceHolder, self).__init__()

    def _register_private_constraints(self, location):
        location.engine().constraints.add(SetPayloadConstraint(location, b''))
    

class Constant(Psifas):
    """
    >>> MY_CONSTANT = Constant(7)
    >>> MY_CONSTANT.parse('')
    7
    >>> MY_CONSTANT.build(7)
    ''
    """    
    spiritual = None
    
    def __init__(self, value):
        super(Constant, self).__init__()
        self.value = value

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetValueConstraint(location, self.value) if not isinstance(self.value, Link) else SetLinkConstraint(location, self.value),
                                          SetPayloadConstraint(location, b''))

class ParentPayload(Psifas):
    r"""
    The payload of the containing psifas.
    Can be used inside Struct:

        >>> my_struct = Struct('first_field', Segment(3),
        ...                    'second_field', Segment(2),
        ...                    'third_field', UBInt(4),
        ...                    'total_payload', ParentPayload())
        >>> parsed_container = my_struct.parse('abc12\x00\x00\x00\x08')
        >>> parsed_container
        Container(...)
        >>> parsed_container.first_field, parsed_container.second_field, parsed_container.third_field
        ('abc', '12', 8)
        >>> parsed_container.total_payload
        'abc12\x00\x00\x00\x08'

        >>> completed_container = my_struct.complete(Container(first_field = 'xyz', second_field = '??', third_field = 2))
        >>> completed_container
        Container(...)
        >>> completed_container.total_payload
        'xyz??\x00\x00\x00\x02'

    Very usefull when we want to see the checksum of the struct:
    
        >>> from functools import partial
        >>> my_struct = Struct('first_field', Segment(3),
        ...                    'second_field', Segment(2),
        ...                    'third_field', UBInt(4),
        ...                    '.total_payload', ParentPayload(),
        ...                    'checksum', Reduce(partial(ModuloAdd, 0x100), Map(Ord, SplitBytes(This/'.total_payload'))))
        >>> parsed_container = my_struct.parse('AaaBB\x00\x00\x00\x02')
        >>> parsed_container
        Container(...)
        >>> parsed_container.checksum
        137
    """
    def __init__(self):
        super(ParentPayload, self).__init__()

    class ParentPayloadInitializeConstraint(SingleExecutionConstraint):
        def _run(self, location):
            if location.parent is None:
                location.engine().postponed_constraints.add(self)
                return False
            location.engine().constraints |= (SetPayloadByValueConstraint(location.parent, location),
                                              SetValueByPayloadConstraint(location, location.parent))
            return True

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, b''),
                                          self.ParentPayloadInitializeConstraint(location))
        
        
class CLink(Constant):
    r"""
    Create operations that refer to other values.
    
    For example, a struct with a Segment field, whose length is determined by
    the value of an field outside:

        >>> my_struct = Struct('size', UBInt(1),
        ...                    'inside', Struct('first_field', UBInt(1),
        ...                                     'my_segment', Segment(This/'.../size')))
        >>> parsed_container = my_struct.parse('\x05\x00hello')
        >>> parsed_container
        Container(...)
        >>> parsed_container.size
        5
        >>> parsed_container.inside.my_segment
        'hello'

        >>> my_struct.build(Container(inside = Container(first_field = 0xFF, my_segment = 'greatsuccess')))
        '\x0c\xffgreatsuccess'
    """
    @classmethod
    def create(cls, direct):
        instance = cls.__new__(cls)
        super(cls, instance).__init__(Link(direct))
        return instance
    
    def __init__(self, target = '.'):
        super(CLink, self).__init__(Link('../' + target))

    def __div__(self, key):
        # overrides the Div operator - use ValueOf(This) instead.
        return CLink.create(self.value.join(Path(key)).to_string())

    def __getattr__(self, key):
        if key.startswith('__'):
            return super(CLink, self).__getattr__(key)
        return self.__div__(key)

This = CLink.create('...')

class Payload(Psifas):
    r"""
    Used for payloads with unknown length:
    
        >>> my_payload = Payload()
        >>> my_payload.parse('read-until-the-end')
        'read-until-the-end'
        >>> my_payload.build('write-until-the-end')
        'write-until-the-end'
        >>> my_struct = Struct('a', Segment(4),
        ...                    'b', Payload(),
        ...                    'c', Segment(4))
        >>> parsed_container = my_struct.parse('????inthemiddle!!!!')
        >>> parsed_container
        Container(...)
        >>> parsed_container.b
        'inthemiddle'
    """
    def __init__(self):
        super(Payload, self).__init__()

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          SetPayloadByValueConstraint(location, location),
                                          SetValueByPayloadConstraint(location, location))

class Leftover(Payload):
    class LeftoverConstraint(SingleExecutionConstraint):
        def _run(self, location):
            payload_offset = location.payload_offset_context().get_value()
            if payload_offset is None:
                return True
            if payload_offset is NumberAbstraction or isinstance(payload_offset, numbers.Number):
                if location.parent is None:
                    location.engine().postponed_constraints.add(self)
                    return False
                location.engine().constraints |= (SetLastPayloadByParentPayloadConstraint(location.parent, location),
                                                  SetLastPayloadOffsetByParentPayloadConstraint(location.parent, location),
                                                  SetParentPayloadByLastPayloadConstraint(location.parent, location),
                                                  self.__class__(location.parent))
                return True
            # payload_offset is Top ?
            return False
            
    def _register_private_constraints(self, location):
        super(Leftover, self)._register_private_constraints(location)
        location.engine().constraints.add(self.LeftoverConstraint(location))

class CString(Psifas):
    r"""
    >>> my_cstring = CString()
    >>> my_cstring.parse('blabla\x00')
    'blabla'
    >>> my_cstring.build('abrakadabra')
    'abrakadabra\x00'
    """
    def __init__(self, terminator = '\x00'):
        if not isinstance(terminator, MetaBytes) or len(terminator) != 1:
            raise TypeError("Invalid terminator %r" % (terminator,))
        super(CString, self).__init__(UniqueField('.leftover', Payload()))
        self.terminator = terminator

    class SetTerminatedValueByValueConstraint(SetValueByValueConstraint):
        def _wrap(self, value, terminator):
            if not isinstance(value, StringAbstraction):
                return SparseString()
            return value + terminator

    class SetValueByTerminatedValueConstraint(SetValueByValueConstraint):
        def _wrap(self, payload, terminator):
            if isinstance(payload, MetaBytes):
                return payload.split(terminator, 1)[0]
            elif isinstance(payload, SparseString):
                for index in xrange(payload.max_length):
                    b = payload.value_at(index)
                    if is_abstract(b):
                        break
                    elif b == terminator:
                        return payload[:index]
                # we did not find a terminator.
                # The length must be at least index + 1
                return SparseString(min_length = index + 1)
            return SparseString()

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          self.SetValueByTerminatedValueConstraint(location, location[0], self.terminator),
                                          self.SetTerminatedValueByValueConstraint(location[0], location, self.terminator))
    

class _FixedSizeSegment(Payload):
    def __init__(self, size):
        super(_FixedSizeSegment, self).__init__()
        self.size = size

    def _register_private_constraints(self, location):
        super(_FixedSizeSegment, self)._register_private_constraints(location)
        location.engine().constraints.add(SetValueConstraint(location, SparseString.from_length(self.size)))

class Segment(Psifas):
    r"""
    Fixed Size Segments:
    
        >>> FIXED_SIZE_SEGMENT = Segment(15)
        >>> FIXED_SIZE_SEGMENT.parse('pypsifas.sf.net')
        'pypsifas.sf.net'
        >>> FIXED_SIZE_SEGMENT.build('!!masterpiece!!')
        '!!masterpiece!!'

    Arbitrary Size Segment:

        >>> my_struct = Struct('my_length', UBInt(1),
        ...                    'my_segment', Segment(This.my_length))
        >>> parsed_container = my_struct.parse('\x06PaScAl')
        >>> parsed_container
        Container(...)
        >>> parsed_container.my_length
        6
        >>> parsed_container.my_segment
        'PaScAl'
        >>> my_struct.build(Container(my_segment = 'WeAreBuildingAPascalString'))
        '\x1aWeAreBuildingAPascalString'

    Knowing that the inner fields are parsed before to wrapping psifas, we parse\build a length-value
    string like this:

        >>> my_length_value = Segment(UBInt(2))
        >>> my_length_value.parse('\x00\x05HELLO')
        'HELLO'
        >>> my_length_value.build('whatever')
        '\x00\x08whatever'
    """
    class SetValueBySizeConstraint(Constraint):
        def _run(self, location):
            size = location[0].context().get_value()
            if not isinstance(size, numbers.Number):
                return
            location.context().set_value(SparseString.from_length(size))

    class SetSizeByValueConstraint(Constraint):
        def _run(self, location):
            value = location.context().get_value()
            if isinstance(value, MetaBytes):
                size = len(value)
            elif isinstance(value, SparseString) and value.min_length == value.max_length:
                size = value.min_length
            else:
                size = NumberAbstraction
            location[0].context().set_value(size)

    def __new__(cls, sizer):
        if isinstance(sizer, numbers.Number):
            return _FixedSizeSegment(sizer)
        return super(Segment, cls).__new__(cls)

    def __init__(self, sizer):
        super(Segment, self).__init__(UniqueField('.size', sizer), UniqueField('.$value', Payload()))

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          self.SetSizeByValueConstraint(location),
                                          self.SetValueBySizeConstraint(location))

class IsEOF(Psifas):
    class SetIsEOFValueConstraint(Constraint):
        def _run(self, location):
            # Assumes the offset is a number or NumberAbstraction
            offset = location.payload_offset_context().get_value()
            if not isinstance(offset, numbers.Number):
                return

            parent_is_eof = location.parent.context('.is_eof#%d' % (location.parent.id,)).get_value()
            if parent_is_eof not in (False, True):
                return
            if not parent_is_eof:
                location.context('.is_eof#%d' % (location.id,)).set_value(False)
                return
            
            parent_payload = location.parent.payload_context().get_value()
            if not isinstance(parent_payload, StringAbstraction):
                return
            parent_payload_min_length, parent_payload_max_length = StringAbstraction.length_range(parent_payload)

            payload = location.payload_context().get_value()
            if not isinstance(payload, StringAbstraction):
                return
            payload_min_length, payload_max_length = StringAbstraction.length_range(payload)

            max_offset = parent_payload_max_length - payload_min_length
            min_offset = parent_payload_min_length - payload_max_length

            if max_offset == min_offset == offset:
                is_eof = True
            elif offset < min_offset:
                is_eof = False
            else:
                return
            location.context('.is_eof#%d' % (location.id,)).set_value(is_eof)

    class SetIsEOFParentPayloadConstraint(Constraint):
        def _run(self, location):
            is_eof = location.context('.is_eof#%d' % (location.id,)).get_value()
            if is_eof not in (False, True):
                return
            
            offset = location.payload_offset_context().get_value()
            if not isinstance(offset, numbers.Number):
                return

            payload = location.payload_context().get_value()
            if not isinstance(payload, StringAbstraction):
                return
            payload_min_length, payload_max_length = StringAbstraction.length_range(payload)

            if is_eof:
                location.parent.payload_context().set_value(SparseString(min_length = offset + payload_min_length,
                                                                         max_length = offset + payload_max_length))
            else:
                if location.parent.context('.is_eof#%d' % (location.parent.id,)).get_value() is True:
                    location.parent.payload_context().set_value(SparseString(min_length = payload_min_length + offset + 1))
                
    class SetIsEOFPayloadConstraint(Constraint):
        def _run(self, location):
            is_eof = location.context('.is_eof#%d' % (location.id,)).get_value()
            if is_eof not in (False, True):
                return
            
            offset = location.payload_offset_context().get_value()
            if not isinstance(offset, numbers.Number):
                return

            parent_payload = location.parent.payload_context().get_value()
            if not isinstance(parent_payload, StringAbstraction):
                return
            parent_payload_min_length, parent_payload_max_length = StringAbstraction.length_range(parent_payload)
            
            if is_eof:
                if parent_payload_max_length >= offset:
                    location.payload_context().set_value(SparseString(min_length = max(0, parent_payload_min_length - offset),
                                                                      max_length = parent_payload_max_length - offset))
            else:
                if parent_payload_max_length > offset:
                    if location.parent.context('.is_eof#%d' % (location.parent.id,)).get_value() is True:
                        location.payload_context().set_value(SparseString(max_length = parent_payload_max_length - offset - 1))
                
    class SetIsEOFOffsetConstraint(Constraint):
        def _run(self, location):
            # Assumes the offset is a number or NumberAbstraction
            offset = location.payload_offset_context().get_value()
            
            is_eof = location.context('.is_eof#%d' % (location.id,)).get_value()
            if is_eof not in (False, True):
                return
                
            parent_payload = location.parent.payload_context().get_value()
            if not isinstance(parent_payload, StringAbstraction):
                return
            parent_payload_min_length, parent_payload_max_length = StringAbstraction.length_range(parent_payload)

            payload = location.payload_context().get_value()
            if not isinstance(payload, StringAbstraction):
                return
            payload_min_length, payload_max_length = StringAbstraction.length_range(payload)

            max_offset = parent_payload_max_length - payload_min_length
            min_offset = parent_payload_min_length - payload_max_length
            
            
            if is_eof:
                if max_offset == min_offset:
                    location.payload_offset_context().set_value(min_offset)
                # FEATURE: create NumberInRange type ?
            else:
                if (max_offset == min_offset == 1) and (location.parent.context('.is_eof#%d' % (location.parent.id,)).get_value() is True):
                    location.payload_offset_context().set_value(0)

    class InitializeIsEOFConstraint(Constraint):
        def __init__(self, location):
            super(IsEOF.InitializeIsEOFConstraint, self).__init__(location)
            self.is_eof_constraints_registered = False
            self.parent_constraints_registered = False
            
        def _run(self, location):
            payload_offset = location.payload_offset_context().get_value()
            if payload_offset is None:
                location.context('.is_eof#%d' % (location.id,)).set_value(True)
                return
            elif not isinstance(payload_offset, numbers.Number) and payload_offset is  not NumberAbstraction:
                return
            # The new constraints can assume that the payload_offset is a number (or NumberAbstraction)
            
            if not self.is_eof_constraints_registered:
                location.engine().constraints |= (IsEOF.SetIsEOFValueConstraint(location),
                                                  IsEOF.SetIsEOFParentPayloadConstraint(location),
                                                  IsEOF.SetIsEOFPayloadConstraint(location),
                                                  IsEOF.SetIsEOFOffsetConstraint(location))
                self.is_eof_constraints_registered = True
                
            if not self.parent_constraints_registered:
                if location.parent is not None:
                    location.engine().constraints.add(IsEOF.InitializeIsEOFConstraint(location.parent))
                    self.parent_constraints_registered = True
                else:
                    location.engine().postponed_constraints.add(self)
        
    def _register_private_constraints(self, location):
        location.engine().constraints |= (self.InitializeIsEOFConstraint(location),
                                          SetPayloadConstraint(location, b''),
                                          SetFieldByValueConstraint(location, '.is_eof#%d' % (location.id,)),
                                          SetValueByFieldConstraint(location, '.is_eof#%d' % (location.id,)))
    
    def __init__(self):
        super(IsEOF, self).__init__()

        
class On(Psifas):
    r"""
    Instead of running the psifas directly on the payload, run it on the value of some field.

        >>> INNER_STRUCT = Struct('num_a', UBInt(2),
        ...                       'num_b', UBInt(2))
        >>> MY_STRUCT = Struct('some_payload', PascalString(),
        ...                    '.$inner', INNER_STRUCT.on(This.some_payload, leftover_field = 'inner_leftover'))
        >>> parsed_container = MY_STRUCT.parse('\x09\x00\x01\x00\x02hello')
        >>> parsed_container
        Container(...)
        >>> parsed_container.some_payload
        '\x00\x01\x00\x02hello'
        >>> parsed_container.num_a, parsed_container.num_b
        (1, 2)
        >>> parsed_container.inner_leftover
        'hello'

        >>> MY_STRUCT.build(Container(num_a = 3, num_b = 4, inner_leftover = 'qqq'))
        '\x07\x00\x03\x00\x04qqq'
    """
    def __init__(self, sub_psifas, target, leftover_field = None):
        if leftover_field is not None:
            sub_psifas = multifield.Struct(Field('.', sub_psifas),
                                           Field(leftover_field, Payload()))
        super(On, self).__init__(UniqueField('.on', target), UniqueField('.value', sub_psifas))
        
    def _register_children_constraints(self, location):
        # treat the first field as the last field
        location.engine().constraints.add(SetPayloadOffsetConstraint(location[0], 0))

        self._register_last_child_payload_constraints(location, location[0])

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          SetPayloadOffsetConstraint(location[1], None),
                                          SetPayloadByValueConstraint(location[1], location[0]),
                                          SetValueByPayloadConstraint(location[0], location[1]),
                                          SetValueByValueConstraint(location, location[1]),
                                          SetValueByValueConstraint(location[1], location))

class Copy(Psifas):
    class SetCopyValueByValueConstraint(SetValueByValueConstraint):
        def _wrap(self, value):
            return deepcopy(value)
    
    def __init__(self, copyof):
        super(Copy, self).__init__(UniqueField('.copy', copyof))

    @property
    def copy(self):
        return self._fields[0].psifas

    def _register_private_constraints(self, location):
        location.engine().constraints |= (self.SetCopyValueByValueConstraint(location, location[0]),
                                          self.SetCopyValueByValueConstraint(location[0], location))

class ValueOf(Psifas):
    def __init__(self, valueof):
        super(ValueOf, self).__init__(UniqueField('.value', valueof))

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetValueByValueConstraint(location, location[0]),
                                          SetValueByValueConstraint(location[0], location))
            
            
class Try(Psifas):
    r"""
    For advance users: Try an inner psifas, and if it fails, try a different one.
    
        >>> MY_TRY = Try(Struct('should_be_seven', UBInt(4), Constant(7)),
        ...              except_psifas = Struct('should_be_seven', Segment(4)),
        ...              exception_field_name = 'why_not')
        >>> parsed_container = MY_TRY.parse('\x00\x00\x00\x07')
        >>> parsed_container
        Container(...)
        >>> parsed_container.should_be_seven
        7
        >>> parsed_container = MY_TRY.parse('\x00\x00\x00\x08')
        >>> parsed_container
        Container(...)
        >>> parsed_container.should_be_seven
        '\x00\x00\x00\x08'

    Works on building too:

        >>> MY_TRY.build(Container(should_be_seven = 7))
        '\x00\x00\x00\x07'
        >>> MY_TRY.build(Container(should_be_seven = 'not!'))
        'not!'

        >>> completed_container = MY_TRY.complete(Container(should_be_seven = 'nah!'))
        >>> completed_container
        Container(...)
        >>> completed_container.should_be_seven
        'nah!'
    """
    
    spiritual = None
    class ExceptConstraint(Constraint):
        def _run(self, try_psifas, parent_location):
            target_location = parent_location[0]
            parent_location.add_sublocations(try_psifas,
                                             [UniqueField('.$except', try_psifas.except_psifas)])
            # add relevant constrains as if the new location is just at location[0]
            sub_location = parent_location[-1]
            try_psifas._register_child_payload_constraints(parent_location, sub_location)
            try_psifas._register_following_payloads_constraints(sub_location, parent_location[1])
            parent_location.engine().constraints.add(SetPayloadOffsetConstraint(sub_location, 0))
    
    class TryConstraint(Constraint):
        def _run(self, try_psifas, parent_location, exception_location):
            exception_class_location = parent_location[1]
            if not exception_class_location.context().get_is_concrete():
                return
            exception_class = exception_class_location.context().get_value()

            engine = parent_location.engine()
            target_location = parent_location[0]

            engine.revert_points.appendleft(ConstraintEngineRevert(engine,
                                                                   exception_class,
                                                                   try_psifas.ExceptConstraint(try_psifas, parent_location),
                                                                   exception_location))
            engine.exception_classes = (exception_class,) + engine.exception_classes
            
            parent_location.add_sublocations(try_psifas,
                                             [UniqueField('.$try', try_psifas.sub_psifas)])
            # add relevant constrains as if the new location is just at location[0]
            sub_location = parent_location[-1]
            try_psifas._register_child_payload_constraints(parent_location, sub_location)
            try_psifas._register_following_payloads_constraints(sub_location, parent_location[1])
            parent_location.engine().constraints.add(SetPayloadOffsetConstraint(sub_location, 0))

    def __init__(self, sub_psifas, except_psifas = Top, exception = PsifasException, exception_field_name = None):
        if except_psifas is Top:
            except_psifas = Psifas()
        elif not isinstance(except_psifas, Psifas):
            except_psifas = Constant(except_psifas)

        if not isinstance(exception, Psifas):
            exception = Constant(exception)

        if exception_field_name is None:
            exception_field = UniqueField('.exception', PayloadlessPlaceHolder())
        else:
            exception_field = Field(exception_field_name, PayloadlessPlaceHolder())
            if sub_psifas.spiritual is True:
                sub_psifas = multifield.Struct('.', sub_psifas,
                                               exception_field_name, Constant(None))
            if except_psifas.spiritual is True:
                except_psifas = multifield.Struct('.', except_psifas,
                                                  exception_field_name, PayloadlessPlaceHolder())
                
        super(Try, self).__init__(UniqueField('.$try', PlaceHolder()),
                                  UniqueField('.exception_class', exception),
                                  exception_field)
        
        self.sub_psifas = sub_psifas
        self.except_psifas = except_psifas

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          self.TryConstraint(self,
                                                             location,
                                                             location[2]))

    def _more_sub_psifases(self):
        return self.sub_psifas, self.except_psifas

def TrySequence(first_psifas, *psifas_sequence):
    if len(psifas_sequence) == 0:
        return first_psifas
    return Try(TrySequence(first_psifas, *psifas_sequence[:len(psifas_sequence)/2]),
               TrySequence(*psifas_sequence[len(psifas_sequence)/2:]))

