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

from datatypes.container import Container
from datatypes.sparse import SparseString
from datatypes.abstract import Top
from constraint import Constraint, SetValueByValueConstraint, SetValueConstraint
from payload_constraint import SetPayloadConstraint
from base import Psifas, UniqueField, Field, On, Payload
import arithmetic

class Spiritualize(Psifas):
    spiritual = True
    def __init__(self, sub_psifas = Top):
        super(Spiritualize, self).__init__(UniqueField('.spiritualize', sub_psifas))

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          SetValueByValueConstraint(location, location[0]),
                                          SetValueByValueConstraint(location[0], location))

class MultiField(Psifas):
    name_validity = {}
    name_validity_max_size = 10**4

    def __init__(self, first_arg, *args, **kw):
        if isinstance(first_arg, Field):
            fields = (first_arg,) + args
        else:
            if isinstance(first_arg, str):
                fields = []
                field_name = first_arg
                for arg in args:
                    if isinstance(arg, str):
                        field_name = arg
                    else:
                        fields.append(Field(field_name, arg))
            else:
                fields = [Field(tup[0], sub_psifas) for tup in (first_arg,) + args for sub_psifas in tup[1:]]
            for field in fields:
                if field.is_nameless() and self.spiritual != field.psifas.spiritual:
                    field.psifas = Spiritualize(field.psifas)

        super(MultiField, self).__init__(*fields, **kw)

    @classmethod
    def is_valid_name(cls, name):
        validity = cls.name_validity.get(name, None)
        if validity is not None:
            return validity
        if len(cls.name_validity) >= cls.name_validity_max_size:
            cls.name_validity.clear()
        # based on the pythonic falseness of ''.isalnum()
        cls.name_validity[name] = validity = name.replace('_', 'a').isalnum() and (not name[0].isdigit()) and not hasattr(Container, name)
        return validity

class Struct(MultiField):
    r"""
    >>> OLD_STRUCT = Struct('segment_a', Segment(4),
    ...                     'segment_b', Segment(4))
    >>> EXTENDED_STRUCT = Struct('header', Segment(6),
    ...                          '.', OLD_STRUCT,
    ...                          'sub_container', OLD_STRUCT)
    >>> c = EXTENDED_STRUCT.parse('HEADerSegASegBabc1ABC2')
    >>> print c
    Container(...)
    >>> sorted([(key, value) for (key, value) in c.__dict__.items() if not key.startswith('_')])
    [('header', 'HEADer'), ('segment_a', 'SegA'), ('segment_b', 'SegB'), ('sub_container', Container(...))]
    >>> sorted([(key, value) for (key, value) in c.sub_container.__dict__.items() if not key.startswith('_')])
    [('segment_a', 'abc1'), ('segment_b', 'ABC2')]
    
    >>> EXTENDED_STRUCT.build(Container(header = 'hhhhhh',
    ...                       sub_container = Container(segment_a = '1234',
    ...                                                 segment_b = '4567'),
    ...                       segment_a = 'abcd',
    ...                       segment_b = 'efgh'))
    'hhhhhhabcdefgh12344567'
    """
    spiritual = True

    class SetFieldValueByContainerConstraint(Constraint):
        def _run(self, location, field_name):
            container = location.context().get_value()
            if not isinstance(container, Container):
                # FEATURE: try to get the attribute from non-Containers ?
                return
            
            if not hasattr(container, field_name):
                return
            location.context(field_name).set_value(getattr(container, field_name))

    class SetContainerByFieldValueConstraint(Constraint):
        def _run(self, location, field_name):
            location.context().set_value(Container(**{field_name: location.context(field_name).get_value()}))
            
    def _register_private_constraints(self, location):
        location.engine().constraints.add(SetPayloadConstraint(location, SparseString()))
        
        super(Struct, self)._register_private_constraints(location)
        
        location.engine().constraints.add(SetValueConstraint(location, Container()))
        for field in self._fields:
            field_name = field.name(self, location)
            if not self.is_valid_name(field_name):
                # '' and '.' field names will work on the same context anyway
                continue
            location.engine().constraints.add(self.SetFieldValueByContainerConstraint(location, field_name))
            location.engine().constraints.add(self.SetContainerByFieldValueConstraint(location, field_name))


class BitsStruct(On):
    r"""
    This struct will be evaluated on the bits of the payload.
    Implements the idea of a Bit Field.

        >>> my_struct = BitsStruct('my_first_field', UBitsInt(4),
        ...                        'my_second_field', SBitsInt(3),
        ...                        'my_rest_of_bits', Segment(9))
        >>> parsed_container = my_struct.parse('\xff\x55') # 1111 111 101010101
        >>> parsed_container
        Container(...)
        >>> '{0:04b}'.format(parsed_container.my_first_field)
        '1111'
        >>> parsed_container.my_second_field
        -1
        >>> parsed_container.my_rest_of_bits
        '101010101'

        >>> my_struct.build(Container(my_first_field = 1, my_second_field = 2, my_rest_of_bits = '000011111'))
        '\x14\x1f'
    """
    def __init__(self, *args, **kws):
        super(BitsStruct, self).__init__(Struct(*args, **kws), arithmetic.BBits())

class ReversedStruct(Struct):
    """
    Reversed struct - first field will be last on the payload.
    """
    def __init__(self, *args, **kws):
        super(ReversedStruct, self).__init__(*args, **kws)
        self._fields = self._fields[::-1]

class ReversedBitsStruct(On):
    def __init__(self, *args, **kws):
        super(ReversedBitsStruct, self).__init__(ReversedStruct(*args, **kws), arithmetic.BBits())
    
class X86BitsStruct(On):
    r"""
    Implements the reveresed little-endian way x86 bitfields are packed.
    For example, the struct:
    struct my_struct_s {
        unsigned a : 6;
        unsigned b : 4;
        unsigned c : 6;
    };
    will be packed into 2 bytes, in the following way:
    * The first byte's 6 lower bits will contain the field a
    * The first byte's 2 upper bits will be b's lower bits.
    * The second byte's 2 lower bits will be b's upper bits.
    * The second byte's 6 upper bits will contain the field c

        >>> import struct
        >>> my_x86_struct = X86BitsStruct('a', UBitsInt(6),
        ...                               'b', UBitsInt(4),
        ...                               'c', UBitsInt(6))
        >>> buf = struct.pack('>H', int('00' + '111111' + '100000' + '01' ,2))
        >>> buf.encode('hex')
        '3f81'
        >>> parsed_container = my_x86_struct.parse(buf)
        >>> parsed_container
        Container(...)
        >>> parsed_container.a == 0b111111
        True
        >>> parsed_container.b == 0b0100
        True
        >>> parsed_container.c == 0b100000
        True
    """
    def __init__(self, *args, **kws):
        super(X86BitsStruct, self).__init__(ReversedStruct(*args, **kws),
                                            arithmetic.BBits(arithmetic.Reversed(Payload())))

