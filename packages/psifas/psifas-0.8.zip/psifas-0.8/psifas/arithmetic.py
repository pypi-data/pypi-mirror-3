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

from datatypes.sparse import SparseString, SparseSequence, SectorCollection
from datatypes.dummy import MetaBytes, optimized_list
from datatypes.abstract import Top, NumberAbstraction, CharAbstraction, StringAbstraction, SequenceAbstraction
from constraint import Constraint, ExternalConstraint, SetValueConstraint
from payload_constraint import SetPayloadConstraint
from base import Psifas, Segment, UniqueField, Payload

from itertools import izip
import operator
import numbers
import struct
import socket
from datetime import datetime, timedelta

UB_SHORT_STRUCT = struct.Struct('>H')
SB_SHORT_STRUCT = struct.Struct('>h')
UL_SHORT_STRUCT = struct.Struct('<H')
SL_SHORT_STRUCT = struct.Struct('<h')

UB_LONG_STRUCT = struct.Struct('>L')
SB_LONG_STRUCT = struct.Struct('>l')
UL_LONG_STRUCT = struct.Struct('<L')
SL_LONG_STRUCT = struct.Struct('<l')

FB_STRUCT = struct.Struct('>f')
FL_STRUCT = struct.Struct('<f')

DB_STRUCT = struct.Struct('>d')
DL_STRUCT = struct.Struct('<d')

S_CHAR_STRUCT = struct.Struct('b')

class UBInt(Psifas):
    r"""
    Unsigned Little Endian.
    
        >>> parsed_num = UBInt(1).parse('\x01')
        >>> print hex(parsed_num)    
        0x1
        >>> parsed_num = UBInt(2).parse('\x01\x02')
        >>> print hex(parsed_num)
        0x102
        >>> parsed_num = UBInt(3).parse('\x01\x02\x03')
        >>> print hex(parsed_num)
        0x10203
        >>> parsed_num = UBInt(4).parse('\x01\x02\x03\x04')
        >>> print hex(parsed_num)
        0x1020304

        >>> UBInt(5).build(2 ** (8 * 5) - 1)
        '\xff\xff\xff\xff\xff'

    UBInt with arbitrary size:

        >>> my_struct = Struct('my_segment', Segment(3),
        ...                    'my_num', UBInt(This.my_segment))
        >>> parsed_container = my_struct.parse('\x00\x00\x02')
        >>> parsed_container
        Container(...)
        >>> parsed_container.my_num
        2
        >>> my_struct.build(Container(my_num = 0xabcd))
        '\x00\xab\xcd'
    """
    def __init__(self, target):
        if isinstance(target, numbers.Number):
            target = Segment(target)
        super(UBInt, self).__init__(UniqueField('payload', target))

    class UBIntParseConstraint(Constraint):
        _parse_by_size = {0: lambda buf: 0,
                          1: ord,
                          2: lambda buf: UB_SHORT_STRUCT.unpack(buf)[0],
                          4: lambda buf: UB_LONG_STRUCT.unpack(buf)[0]}

        @staticmethod
        def _parse_iteration(x, y):
            return (x << 8) + ord(y)
    
        @classmethod
        def parse_number(cls, buf):
            return reduce(cls._parse_iteration, buf, 0)
        
        def _run(self, location):
            buf = location[0].context().get_value()
            if not isinstance(buf, MetaBytes):
                return
            location.context().set_value(self._parse_by_size.get(len(buf), self.parse_number)(buf))

    parse_constraint_class = UBIntParseConstraint

    class UBIntBuildConstraint(Constraint):
        _build_by_size = {0: lambda num: '',
                          1: chr,
                          2: UB_SHORT_STRUCT.pack,
                          4: UB_LONG_STRUCT.pack}
    
        @staticmethod
        def build_number(number, size):
            return ''.join(chr((number >> (8 * index)) & 0xFF) for index in xrange(size - 1, -1, -1))

        def _run(self, location):
            value = location.context().get_value()
            if not isinstance(value, numbers.Number):
                return
            buf = location[0].context().get_value()
            if isinstance(buf, MetaBytes):
                buf_size = len(buf)
            elif isinstance(buf, SparseString) and buf.min_length == buf.max_length:
                buf_size = buf.min_length
            else:
                return
            build_function = self._build_by_size.get(buf_size, None)
            if build_function is not None:
                buf = build_function(value)
            else:
                buf = self.build_number(value, buf_size)
            
            location[0].context().set_value(buf)

    build_constraint_class = UBIntBuildConstraint
            
    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetValueConstraint(location, NumberAbstraction),
                                          SetValueConstraint(location[0], SparseString()),
                                          self.parse_constraint_class(location),
                                          self.build_constraint_class(location))
            

class ULInt(UBInt):
    r"""
    Unsigned Little Endian
    
        >>> parsed_num = ULInt(1).parse('\x01')
        >>> print hex(parsed_num)
        0x1
        >>> parsed_num = ULInt(2).parse('\x01\x02')
        >>> print hex(parsed_num)
        0x201
        >>> parsed_num = ULInt(3).parse('\x01\x02\x03')
        >>> print hex(parsed_num)
        0x30201
        >>> parsed_num = ULInt(4).parse('\x01\x02\x03\x04')
        >>> print hex(parsed_num)
        0x4030201

        >>> ULInt(5).build(2 ** (8 * 5) - 1 - 0xff)
        '\x00\xff\xff\xff\xff'

    ULInt with arbitrary size:

        >>> my_struct = Struct('my_segment', Segment(3),
        ...                    'my_num', ULInt(This.my_segment))
        >>> parsed_container = my_struct.parse('\x07\x00\x00')
        >>> parsed_container
        Container(...)
        >>> parsed_container.my_num
        7
        >>> my_struct.build(Container(my_num = 0xabcd))
        '\xcd\xab\x00'
    """    
    class ULIntParseConstraint(UBInt.UBIntParseConstraint):
        _parse_by_size = {0: lambda buf: 0,
                          1: ord,
                          2: lambda buf: UL_SHORT_STRUCT.unpack(buf)[0],
                          4: lambda buf: UL_LONG_STRUCT.unpack(buf)[0]}

        @classmethod
        def parse_number(cls, buf):
            return reduce(cls._parse_iteration, reversed(buf), 0)

    parse_constraint_class = ULIntParseConstraint

    class ULIntBuildConstraint(UBInt.UBIntBuildConstraint):
        _build_by_size = {0: lambda num: '',
                          1: chr,
                          2: UL_SHORT_STRUCT.pack,
                          4: UL_LONG_STRUCT.pack}

        @staticmethod
        def build_number(number, size):
            return ''.join(chr((number >> (8 * index)) & 0xFF) for index in xrange(size))

    build_constraint_class = ULIntBuildConstraint

class SBInt(UBInt):
    r"""
    Signed Big Endian.
    
        >>> parsed_num = SBInt(1).parse('\x01')
        >>> print hex(parsed_num)    
        0x1
        >>> parsed_num = SBInt(2).parse('\x01\x02')
        >>> print hex(parsed_num)
        0x102
        >>> parsed_num = SBInt(2).parse('\xff\xff')
        >>> print hex(parsed_num)
        -0x1
        >>> SBInt(2).build(-2)
        '\xff\xfe'
    """
    class SBIntParseConstraint(UBInt.UBIntParseConstraint):
        _parse_by_size = {0: lambda buf: 0,
                          1: lambda buf: S_CHAR_STRUCT.unpack(buf)[0],
                          2: lambda buf: SB_SHORT_STRUCT.unpack(buf)[0],
                          4: lambda buf: SB_LONG_STRUCT.unpack(buf)[0]}

        @classmethod
        def parse_number(cls, buf):
            return reduce(cls._parse_iteration, buf[1:], S_CHAR_STRUCT.unpack(buf[0])[0])

    parse_constraint_class = SBIntParseConstraint

    class SBIntBuildConstraint(UBInt.UBIntBuildConstraint):
        _build_by_size = {0: lambda num: '',
                          1: S_CHAR_STRUCT.pack,
                          2: SB_SHORT_STRUCT.pack,
                          4: SB_LONG_STRUCT.pack}

        @staticmethod
        def build_number(number, size):
            return UBInt.UBIntBuildConstraint.build_number(number % (0x100 ** size), size)

    build_constraint_class = SBIntBuildConstraint

class SLInt(UBInt):
    r"""
    Signed Little Endian.
    
        >>> parsed_num = SLInt(1).parse('\x01')
        >>> print hex(parsed_num)    
        0x1
        >>> parsed_num = SLInt(2).parse('\x01\x02')
        >>> print hex(parsed_num)
        0x201
        >>> parsed_num = SLInt(2).parse('\xff\xff')
        >>> print hex(parsed_num)
        -0x1
        >>> SLInt(4).build(-2)
        '\xfe\xff\xff\xff'
    """
    class SLIntParseConstraint(UBInt.UBIntParseConstraint):
        _parse_by_size = {0: lambda buf: 0,
                          1: lambda buf: S_CHAR_STRUCT.unpack(buf)[0],
                          2: lambda buf: SL_SHORT_STRUCT.unpack(buf)[0],
                          4: lambda buf: SL_LONG_STRUCT.unpack(buf)[0]}

        @classmethod
        def parse_number(cls, buf):
            return reduce(cls._parse_iteration, buf[1:], S_CHAR_STRUCT.unpack(buf[0])[0])

    parse_constraint_class = SLIntParseConstraint

    class SLIntBuildConstraint(UBInt.UBIntBuildConstraint):
        _build_by_size = {0: lambda num: '',
                          1: S_CHAR_STRUCT.pack,
                          2: SL_SHORT_STRUCT.pack,
                          4: SL_LONG_STRUCT.pack}

        @staticmethod
        def build_number(number, size):
            return ULInt.ULIntBuildConstraint.build_number(number % (0x100 ** size), size)

    build_constraint_class = SLIntBuildConstraint

class UBitsInt(UBInt):
    r"""
    Unsigned Bits-Integer.
    See BitsStruct in multifield.py for more examples.

       >>> UBitsInt(4).parse('0010')
       2
       >>> UBitsInt(2).build(3)
       '11'
    """
    class UBitsIntParseConstraint(UBInt.UBIntParseConstraint):
        _parse_by_size = {0: lambda buf: 0}

        @classmethod
        def parse_number(cls, buf):
            return int(buf, 2)

    parse_constraint_class = UBitsIntParseConstraint

    class UBitsIntBuildConstraint(UBInt.UBIntBuildConstraint):
        _build_by_size = {0: lambda num: ''}

        @staticmethod
        def build_number(number, size):
            return '{0:b}'.format(number).zfill(size)

    build_constraint_class = UBitsIntBuildConstraint

class SBitsInt(UBInt):
    r"""
    Signed Bits-Integer.
    See BitsStruct in multifield.py for more examples.

       >>> SBitsInt(4).parse('1110')
       -2
       >>> SBitsInt(4).build(1)
       '0001'
    """
    class SBitsIntParseConstraint(UBInt.UBIntParseConstraint):
        _parse_by_size = {0: lambda buf: 0}

        @classmethod
        def parse_number(cls, buf):
            num = int(buf[1:], 2)
            if buf[0] == '0':
                return num
            else:
                return num - (1 << (len(buf) - 1))

    parse_constraint_class = SBitsIntParseConstraint

    class SBitsIntBuildConstraint(UBInt.UBIntBuildConstraint):
        _build_by_size = {0: lambda num: ''}

        @staticmethod
        def build_number(number, size):
            return '{0:b}'.format(number & ((1 << size) - 1)).zfill(size)

    build_constraint_class = SBitsIntBuildConstraint


class Operator1Abstract(Psifas):
    def __init__(self, arg):
        super(Operator1Abstract, self).__init__(UniqueField('%s_of' % (self.__class__.__name__.lower(),), arg))

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          ExternalConstraint(self, 'run_parse', location),
                                          ExternalConstraint(self, 'run_build', location))

    def run_parse(self, location):
        location.context().set_value(self._parse(location[0].context().get_value()))
        
    def run_build(self, location):
        location[0].context().set_value(self._build(location.context().get_value()))

    def _parse(self, value):
        return Top

    def _build(self, value):
        return Top

class Operator1(Operator1Abstract):
    def run_parse(self, location):
        if not location[0].context().get_is_concrete():
            return
        return super(Operator1, self).run_parse(location)

    def run_build(self, location):
        if not location.context().get_is_concrete():
            return
        return super(Operator1, self).run_build(location)

class Operator2Abstract(Psifas):
    def __init__(self, left, right):
        super(Operator2Abstract, self).__init__(UniqueField('%s_left'  % (self.__class__.__name__.lower(),), left),
                                                UniqueField('%s_right'  % (self.__class__.__name__.lower(),), right))

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          ExternalConstraint(self, 'run_parse', location),
                                          ExternalConstraint(self, 'run_build_left', location),
                                          ExternalConstraint(self, 'run_build_right', location))

    def run_parse(self, location):
        location.context().set_value(self._parse(location[0].context().get_value(),
                                                 location[1].context().get_value()))

    def run_build_left(self, location):
        location[0].context().set_value(self._build_left(location.context().get_value(),
                                                         location[1].context().get_value()))

    def run_build_right(self, location):
        location[1].context().set_value(self._build_right(location.context().get_value(),
                                                          location[0].context().get_value()))

    def _parse(self, left, right):
        return Top
    
    def _build_left(self, value, right):
        return Top

    def _build_right(self, value, left):
        return Top

class Operator2(Operator2Abstract):
    def run_parse(self, location):
        if not location[0].context().get_is_concrete() or not location[1].context().get_is_concrete():
            return
        return super(Operator2, self).run_parse(location)

    def run_build_left(self, location):
        if not location.context().get_is_concrete() or not location[1].context().get_is_concrete():
            return
        return super(Operator2, self).run_build_left(location)

    def run_build_right(self, location):
        if not location.context().get_is_concrete() or not location[0].context().get_is_concrete():
            return
        return super(Operator2, self).run_build_right(location)

class OperatorNAbstract(Psifas):
    def __init__(self, *args):
        super(OperatorNAbstract, self).__init__(*(UniqueField('%s_arg%d' % (self.__class__.__name__.lower(), index), arg)
                                                  for (index, arg) in enumerate(args)))

    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          ExternalConstraint(self, 'run_parse', location))
        location.engine().constraints |= [ExternalConstraint(self, 'run_build', location, index)
                                          for index in xrange(len(self._fields))]

    def run_parse(self, location):
        location.context().set_value(self._parse(*(sub_location.context().get_value()
                                                   for sub_location in location)))

    def run_build(self, location, index):
        location[index].context().set_value(self._build(index,
                                                        location.context().get_value(),
                                                        *(sub_location.context().get_value()
                                                          for sub_index, sub_location in enumerate(location)
                                                          if sub_index != index)))
                                        
    def _parse(self, *sub_values):
        return Top
    
    def _build(self, index, value, *sub_values):
        return Top


class OperatorN(OperatorNAbstract):
    def run_parse(self, location):
        if not all(sub_location.context().get_is_concrete() for sub_location in location):
            return
        return super(OperatorN, self).run_parse(location)

    def run_build(self, location, index):
        if not location.context().get_is_concrete():
            return
        if not all(sub_location.context().get_is_concrete()
                   for sub_index, sub_location in enumerate(location)
                   if sub_index != index):
            return
        return super(OperatorN, self).run_build(location, index)

class Decipher(Psifas):
    def __init__(self, *args):
        super(Decipher, self).__init__(*(UniqueField('%s_arg%d' % (self.__class__.__name__.lower(), index), arg)
                                         for (index, arg) in enumerate(args)))
    
    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          ExternalConstraint(self, 'run_decipher', location))
        
    def run_decipher(self, location):
        new_values = tuple(self.decipher(location.context().get_value(),
                                        *(sub_location.context().get_value() for sub_location in location)))
        location.context().set_value(new_values[0])
        for new_value, sub_location in izip(new_values[1:], location):
            sub_location.context().set_value(new_value)
    
    def decipher(self, value, *sub_values):
        # override this function.
        return (value,) + sub_values
    
class Call(OperatorN):
    def _parse(self, func, *args):
        return func(*args)

class Sum(Operator1):
    r"""
    Usefull together with SequenceOf. For example:

        >>> MY_STRUCT = Struct('a', UBInt(1),
        ...                    'b', UBInt(2),
        ...                    'c', UBInt(4),
        ...                    'abc_sum', Sum(SequenceOf(This.a, This.b, This.c)))
        >>> parsed_container = MY_STRUCT.parse('\x00\x00\x02\x00\x00\x00\x06')
        >>> parsed_container
        Container(...)
        >>> parsed_container.abc_sum
        8
    """
    _parse = sum

class ModuloAdd(OperatorN):
    r"""
    Usefull to verify and auto-fill checksums!
        >>> from functools import partial
        >>> MY_STRUCT = Struct('checksum', UBInt(1), Reduce(partial(ModuloAdd, 0x100), Map(Ord, SplitBytes(This/'.checksumed_payload'))),
        ...                   '.', Struct('a', Segment(5),
        ...                               'b', UBInt(1),
        ...                               'c', PascalString(),
        ...                               '.checksumed_payload', ParentPayload()))
        >>> MY_STRUCT.build(Container(a = 'aaaaa', b = 7, c = 'hi')) # auto-fill checksum
        '\xbfaaaaa\x07\x02hi'
        >>> MY_STRUCT.parse('\x2faaaaa\x07\x03bye') # correct checksum
        Container(...)
        >>> try:
        ...     MY_STRUCT.parse('\x00aaaaa\x07\x03bye') # incorrect checksum
        ... except Contradiction, e:
        ...     print 'Expected Exception: %r' % (e,)
        ... else:
        ...     print 'expected exception not raised'
        Expected Exception: ...
    """
    def _parse(self, modulo, *args):
        return sum(args) % modulo

    def _build(self, index, total_sum, *args):
        if index == 0:
            # we cannot build the modulo value
            return NumberAbstraction
        return (total_sum - sum(args[1:])) % args[0]

class Length(Decipher):
    r"""
    Usefull to verify and auto-fill length:

        >>> MY_STRUCT = Struct('length', UBInt(1), Length(This/'.length_payload'),
        ...                    '.', Struct('a', Segment(3),
        ...                                'b', UBInt(1),
        ...                                'c', PascalString(),
        ...                                '.length_payload', ParentPayload()))
        >>> MY_STRUCT.build(Container(a = '123', b = 0, c = 'hi'))
        '\x07123\x00\x02hi'
    """
    def __init__(self, arg):
        super(Length, self).__init__(arg)
        
    def decipher(self, length, value):
        new_length = NumberAbstraction
        new_value = Top
        
        if isinstance(value, StringAbstraction):
            min_length, max_length = StringAbstraction.length_range(value)
            if min_length == max_length:
                new_length = min_length
            if isinstance(length, numbers.Number):
                new_value = SparseString.from_length(length)
        elif isinstance(value, SequenceAbstraction):
            min_length, max_length = SequenceAbstraction.length_range(value)
            if min_length == max_length:
                new_length = min_length
            if isinstance(length, numbers.Number):
                new_value = SparseSequence.from_length(length)
        return (new_length, new_value)

Len = Length

class Negative(Operator1):
    r"""
    Mathematical operands can be used on psifas to create other psifases:

        >>> MY_NUMBER = 7 - UBInt(1)
        >>> MY_NUMBER.parse('\x06')
        1
        >>> MY_NUMBER.build(0)
        '\x07'
    """
    _parse = _build = operator.neg
Psifas.__neg__ = lambda self: Negative(self)

class Not(Operator1):
    _parse = operator.not_
    # cannot build: not(not(3)) != 3
Psifas.__not__ = Not

class Invert(Operator1):
    r"""
    Example:

        >>> MY_NUMBER = ~UBInt(1)
        >>> MY_NUMBER.parse('\x00')
        -1
        >>> MY_NUMBER.build(-0x0f)
        '\x0e'
    """
    _parse = _build = operator.inv
Psifas.__invert__ = lambda self: Invert(self)

class Reversed(Operator1Abstract):
    r"""
    Reverse the sequence:

        >>> MY_REVERSE = Reversed(PascalString())
        >>> MY_REVERSE.parse('\x0bhello world')
        'dlrow olleh'
        >>> MY_REVERSE.build('reverse')
        '\x07esrever'
    """
    def reverse(self, value):
        if not isinstance(value, (StringAbstraction, SequenceAbstraction)):
            return Top
        return value[::-1]
    _parse = _build = reverse

Reverse = Reversed

class BBits(Operator1Abstract):
    r"""
    Converts bytes payload to bits payload.
    See BitsStruct in multifield.py
    """
    # Big Endian - for every byte, the most segnificant bit comes first
    def __init__(self, inner = None):
        if inner is None:
            inner = Payload()
        elif isinstance(inner, numbers.Number):
            inner = Segment(inner)
        super(BBits, self).__init__(inner)

    _byte_to_bits = dict((chr(num), '{0:08b}'.format(num))
                         for num in xrange(0x100))
    _bits_to_byte = dict((tuple('{0:08b}'.format(num)), chr(num))
                         for num in xrange(0x100))

    def _parse(self, bytes):
        if isinstance(bytes, MetaBytes):
            return reduce(operator.add, (self._byte_to_bits[c] for c in bytes))
        elif isinstance(bytes, SparseString):
            value = optimized_list([Top]) * (len(bytes.value) * 8)
            for sector_start, sector_end in bytes.sectors:
                for index in xrange(sector_start, sector_end):
                    bits = self._byte_to_bits.get(bytes.value[index], None)
                    if bits is not None:
                        value[index * 8:(index + 1) * 8] = bits
            return SparseString(value,
                                min_length = bytes.min_length * 8,
                                max_length = bytes.max_length * 8,
                                sectors = [(start * 8, end * 8) for (start, end) in bytes.sectors])
        return Top

    def _build(self, bits):
        if isinstance(bits, MetaBytes):
            return SparseString(optimized_list(self._bits_to_byte.get(tuple(bits[index:index+8]), CharAbstraction)
                                               for index in xrange(0, len(bits), 8)),
                                min_length = len(bits) / 8,
                                max_length = len(bits) / 8)
        elif isinstance(bits, SparseString):
            # filter out small sectors:
            sectors = SectorCollection([(start / 8, end / 8) for (start, end) in bits.sectors if end - start >= 8])
            value = optimized_list([CharAbstraction]) * (len(bits.value) / 8)
            for sector_start, sector_end in sectors:
                for index in xrange(sector_start, sector_end):
                    value[index] = self._bits_to_byte.get(tuple(bits.value[index * 8:(index + 1) * 8]), CharAbstraction)
            return SparseString(value,
                                min_length = bits.min_length / 8,
                                max_length = bits.max_length / 8,
                                sectors = sectors)
        else:
            return SparseString()

class LBits(BBits):
    _byte_to_bits = dict((chr(num), '{0:08b}'.format(num)[::-1])
                         for num in xrange(0x100))
    _bits_to_byte = dict((tuple('{0:08b}'.format(num))[::-1], chr(num))
                         for num in xrange(0x100))

class FlagBit(Operator1):
    def __init__(self):
        super(FlagBit, self).__init__(Segment(1))

    def _parse(self, byte):
        return byte != '0'

    def _build(self, flag):
        return ('1' if flag else '0')

class Concatenate(Operator2Abstract):
    def _parse(self, left, right):
        if ((isinstance(left, SequenceAbstraction) and isinstance(right, SequenceAbstraction)) or
            (isinstance(left, StringAbstraction) and isinstance(right, StringAbstraction))):
            return left + right
        return Top
    
    @staticmethod
    def _build_left(value, right):
        if isinstance(value, SequenceAbstraction) and isinstance(right, SequenceAbstraction):
            value_min_length, value_max_length = SequenceAbstraction.length_range(value)
            right_min_length, right_max_length = SequenceAbstraction.length_range(right)
            if isinstance(value, SparseSequence):
                value = value.value
            min_length = max(value_min_length - right_max_length, 0)
            max_length = max(value_max_length - right_min_length, 0)
            if min_length > max_length:
                return Top
            return SparseSequence(value, min_length = min_length, max_length = max_length)
        if isinstance(value, StringAbstraction) and isinstance(right, StringAbstraction):
            value_min_length, value_max_length = StringAbstraction.length_range(value)
            right_min_length, right_max_length = StringAbstraction.length_range(right)
            if isinstance(value, SparseString):
                value = value.value
            min_length = max(value_min_length - right_max_length, 0)
            max_length = max(value_max_length - right_min_length, 0)
            if min_length > max_length:
                return Top
            return SparseString(value, min_length = min_length, max_length = max_length)
        return Top

    @staticmethod
    def _build_right(value, left):
        if isinstance(value, SequenceAbstraction) and isinstance(left, SequenceAbstraction):
            left_min_length, left_max_length = SequenceAbstraction.length_range(left)
        elif isinstance(value, StringAbstraction) and isinstance(left, StringAbstraction):
            left_min_length, left_max_length = StringAbstraction.length_range(left)
        else:
            return Top
        if left_min_length != left_max_length:
            return Top
        return value[left_min_length:]

Psifas.__concat__ = lambda a,b: Concatenate(a,b)

class Add(Operator2Abstract):
    _parse = operator.add

    def _build_symmetric(self, value, arg):
        if isinstance(value, numbers.Number) and isinstance(arg, numbers.Number):
            return value - arg
        if isinstance(value, (datetime, timedelta)):
            try:
                return value - arg
            except TypeError:
                pass
        return Top

    def _parse(self, left, right):
        if isinstance(left, (StringAbstraction, SequenceAbstraction)):
            return Concatenate._parse(left, right)
        if isinstance(left, numbers.Number) and isinstance(right, numbers.Number):
            return left + right
        if isinstance(left, (datetime, timedelta)):
            try:
                return left + right
            except TypeError:
                pass
        return Top

    def _build_left(self, value, right):
        if isinstance(value, (StringAbstraction, SequenceAbstraction)):
            return Concatenate._build_left(value, right)
        return self._build_symmetric(value, right)
    
    def _build_right(self, value, left):
        if isinstance(value, (StringAbstraction, SequenceAbstraction)):
            return Concatenate._build_right(value, left)
        return self._build_symmetric(value, left)
Psifas.__add__ = lambda a, b: Add(a,b)

class Multiply(Operator2):
    _parse = operator.mul

    def _build(self, value, other):
        if other == 0:
            return Top
        if isinstance(value, numbers.Number):
            if value % other == 0:
                return value / other
            return operator.truediv(value, other)
        if operator.isSequenceType(value):
            if isinstance(other, numbers.Number):
                if len(value) % other == 0:
                    if value == value[:len(value) / other] * other:
                        return value[:len(value) / other]
            elif operator.isSequenceType(other):
                if (len(other) != 0) and (len(value) % len(other) == 0):
                    if tuple(value) == tuple(other) * (len(value) / len(other)):
                        return len(value) / len(other)
        return Top

    _build_left = _build_right = _build
Psifas.__mul__ = lambda a, b: Multiply(a,b)

class Mod(Operator2):
    _parse = operator.mod
Psifas.__mod__ = lambda a,b: Mod(a,b)

class Div(Operator2):
    _parse = operator.div
Psifas.__div__ = lambda a,b: Div(a,b)

class And_(Operator2):
    _parse = operator.and_
Psifas.__and__ = lambda a,b: And_(a,b)

class Or_(Operator2):
    _parse = operator.or_
Psifas.__or__ = lambda a,b: Or_(a,b)


class Equal(Operator2):
    _parse = operator.eq

    def _build(self, value, arg):
        if value is True:
            return arg
        return Top

    _build_right = _build_left = _build

class GreaterThan(Operator2):
    _parse = operator.gt
Psifas.__gt__ = lambda a, b: GreaterThan(a, b)

class GreaterEqual(Operator2):
    _parse = operator.ge
Psifas.__ge__ = lambda a, b: GreaterEqual(a, b)

class LessEqual(Operator2):
    _parse = operator.le
Psifas.__le__ = lambda a, b: LessEqual(a, b)

class LessThan(Operator2):
    _parse = operator.lt
Psifas.__lt__ = lambda a, b: LessThan(a, b)

class LeftShift(Operator2):
    _parse = operator.lshift

    def _build_left(self, value, right):
        return value >> right
Psifas.__lshift__ = lambda a, b: LeftShift

class RightShift(Operator2):
    _parse = operator.rshift
Psifas.__rshift__ = lambda a, b: RightShift
        
class Contains(Operator2):
    _parse = operator.contains





class Ord(Operator1):
    _parse = ord
    _build = chr

class Chr(Operator1):
    _parse = chr
    _build = ord

class Encode(Operator2):
    def _parse(self, value, enc):
        return value.encode(enc)

    def _build_left(self, value, enc):
        return value.decode(enc)

class JoinBytes(Operator1Abstract):
    """
    converts a sequence of chars to a string.
    """
    def _parse(self, value):
        if not isinstance(value, SequenceAbstraction):
            return Top
        min_length, max_length = SequenceAbstraction.length_range(value)
        if isinstance(value, SparseSequence):
            sectors = value.sectors
            value = value.value
        else:
            sectors = None
        return SparseString(value, min_length = min_length, max_length = max_length, sectors = sectors)
            
    def _build(self, value):
        if not isinstance(value, StringAbstraction):
            return Top
        min_length, max_length = StringAbstraction.length_range(value)
        if isinstance(value, SparseString):
            sectors = value.sectors
            value = value.value
        else:
            sectors = None
        return SparseSequence(value, min_length = min_length, max_length = max_length, sectors = sectors)

class SplitBytes(JoinBytes):
    _parse = JoinBytes._build
    _build = JoinBytes._parse

class Upper(Operator1):
    def _parse(self, value):
        return value.upper()

class Lower(Operator1):
    def _parse(self, value):
        return value.lower()

class LowerToUpper(Operator1):
    def _parse(self, value):
        return value.upper()

    def _build(self, value):
        return value.lower()

class UpperToLower(LowerToUpper):
    _parse = LowerToUpper._build
    _build = LowerToUpper._parse

class ToSigned(Operator2):
    """
    converts unsigned numbers to signed numbers
    """
    def _parse(self, unsigned_number, number_of_bits):
        return ((unsigned_number - 2 **(number_of_bits - 1)) % (2**number_of_bits)) - 2 ** (number_of_bits - 1)

    def _build_left(self, signed_number, number_of_bits):
        return signed_number % (2**number_of_bits)

class ToUnsigned(ToSigned):
    _parse = ToSigned._build_left
    _build_left = ToSigned._parse

class IPAddress(Operator1):
    def __init__(self):
        super(IPAddress, self).__init__(Segment(4))

    _parse = socket.inet_ntoa
    _build = socket.inet_aton

class IPChecksum(Operator1):
    @staticmethod
    def leftover_sum(a, b):
        """
        Assumes a, b < 0x10000
        """
        return ((a + b) & 0xFFFF) + ((a + b) >> 1)

    def _parse(self, buf):
        if len(buf) % 2 == 1:
            buf += '\x00'
        return 0xFFFF - reduce(self.leftover_sum , struct.unpack('>%dH' % (len(buf) / 2,), buf))

class Byte(Operator1Abstract):
    """
    Notice the difference between a byte and a string.
    a string is a sequence of bytes, but basically a byte is not a string of length 1.
    """
    def __init__(self, inner = None):
        if inner is None:
            inner = Segment(1)
        super(Byte, self).__init__(inner)

    def _parse(self, buf):
        if not isinstance(buf, MetaBytes) or len(buf) != 1:
            return CharAbstraction
        return buf

    def _build(self, byte):
        if not isinstance(byte, MetaBytes) or len(byte) != 1:
            return SparseString(min_length = 1, max_length = 1)
        return byte
        
        
