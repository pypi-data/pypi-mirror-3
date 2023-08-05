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

from base import Psifas, Constant, Field, UniqueField, PlaceHolder
from datatypes.abstract import Top, NumberAbstraction, is_abstract
from constraint import Constraint, SetValueByValueConstraint
from payload_constraint import SetPayloadOffsetConstraint

class MappingSwitch(Psifas):
    r"""
    For simple uses, see class Switch.
    Unlike switch, this class lets you define a choice function instead of dictionary.

        >>> class MyMappingSwitch(MappingSwitch):
        ...     def mapping(self, switch_byte):
        ...         if is_abstract(switch_byte):
        ...             return super(MyMappingSwitch, self).mapping(switch_byte)
        ...         if isinstance(switch_byte, bytes) and switch_byte.isdigit():
        ...             return Map(Ord, SplitBytes(Payload())) # parse the rest as a sequence of numbers
        ...         if switch_byte == 'N':
        ...             return UBInt(4) # parse the rest 4 bytes as a single number.
        ...         return Payload() # parse the rest as a string.
        ...     def reverse_mapping(self, solution_value):
        ...         if isinstance(solution_value, int):
        ...             return 'N'
        ...         # we can figure out if the switch_byte should be a digit or not, but we cannot give
        ...         # an exact value:
        ...         return super(MyMappingSwitch, self).reverse_mapping(solution_value)
        >>> my_switch = Struct('deciding_byte', Byte(),
        ...                    'my_value', MyMappingSwitch(This.deciding_byte))
        >>> parsed_container = my_switch.parse('0\x00\x01\x02\x03')
        >>> parsed_container
        Container(...)
        >>> list(parsed_container.my_value)
        [0, 1, 2, 3]
        >>> parsed_container = my_switch.parse('N\x00\x00\x00\x09')
        >>> parsed_container
        Container(...)
        >>> parsed_container.my_value
        9
        >>> parsed_container = my_switch.parse('?someleftover')
        >>> parsed_container
        Container(...)
        >>> parsed_container.my_value
        'someleftover'

        >>> my_switch.build(Container(deciding_byte = 'x', my_value = 'WAKAWAKA'))
        'xWAKAWAKA'
        >>> my_switch.build(Container(deciding_byte = '1', my_value = [3, 2, 1]))
        '1\x03\x02\x01'
        >>> my_switch.build(Container(my_value = 0xAA)) # auto-complete deciding byte!
        'N\x00\x00\x00\xaa'
    """
    def mapping_location(self, location):
        """
        maps a location to a Psifas
        """
        return self.mapping(location[0].context().get_value())

    def mapping(self, switch_case):
        """
        maps a switch-value to a Psifas
        """
        return PlaceHolder()

    def reverse_mapping_location(self, location):
        solution_value = location[1].context().get_value()
        if solution_value is Top:
            return Top
        return self.reverse_mapping_abstract(solution_value)

    def reverse_mapping_abstract(self, solution_value):
        if is_abstract(solution_value):
            return Top
        return self.reverse_mapping(solution_value)

    def reverse_mapping(self, solution_value):
        return Top

    class InitializeSwitchConstraint(Constraint):
        def __init__(self, *parameters):
            super(MappingSwitch.InitializeSwitchConstraint, self).__init__(*parameters)
            # this container must be a list and not a set - the subpsifases may be regenerated
            # every time mapping_location is called, and we don't want to register psifases
            # that were already generated before.
            self.returned_psifases = []
            
        def _run(self, psifas, location):
            chosen_psifas = psifas.mapping_location(location)
            if chosen_psifas in self.returned_psifases:
                # if its equal to one of the already used psifases - continue
                return
            
            case_location = location[0]
            value_location = location[1]
            location.add_sublocations(psifas,
                                      [UniqueField('.%s_value' % (psifas.__class__.__name__,), chosen_psifas)])
            # add relevant constrains as if the new location is just after location[0]
            sub_location = location[-1]
            location.engine().constraints.add(SetPayloadOffsetConstraint(sub_location, NumberAbstraction))
            psifas._register_following_payloads_constraints(case_location, sub_location)
            
            psifas._register_last_child_payload_constraints(location, sub_location)
            self.returned_psifases.append(chosen_psifas)

    class SwitchReverseConstraint(Constraint):
        def _run(self, psifas, location):
            reversed_value = psifas.reverse_mapping_location(location)
            location[0].context().set_value(reversed_value)

    def __init__(self, switch_field):
        if not isinstance(switch_field, Field):
            switch_field = UniqueField('.%s_case' % (self.__class__.__name__,), switch_field)
        super(MappingSwitch, self).__init__(switch_field, UniqueField('.%s_value' % (self.__class__.__name__,), PlaceHolder()))
        
    def _register_private_constraints(self, location):
        super(MappingSwitch, self)._register_private_constraints(location)
        location.engine().constraints |= (self.InitializeSwitchConstraint(self, location),
                                          self.SwitchReverseConstraint(self, location),
                                          SetValueByValueConstraint(location, location[1]),
                                          SetValueByValueConstraint(location[1], location))

class Dynamic(MappingSwitch):
    r"""
    Use evaluated values as psifases for further parsing/building:

        >>> MY_STRUCT = Struct('endian', Byte(),
        ...                    'endian_psifas', Switch(This.endian,
        ...                                            {'>': Constant(UBInt(4)),
        ...                                             '<': Constant(ULInt(4))}),
        ...                    'first_field', Dynamic(This.endian_psifas),
        ...                    'second_field', Dynamic(This.endian_psifas))
        >>> parsed_container = MY_STRUCT.parse('>\x00\x00\x00\x01\x00\x00\x00\x02')
        >>> parsed_container
        Container(...)
        >>> parsed_container.first_field, parsed_container.second_field
        (1, 2)
        >>> MY_STRUCT.build(Container(endian = '<', first_field = 3, second_field = 4))
        '<\x03\x00\x00\x00\x04\x00\x00\x00'
        
    """
    def mapping(self, value):
        if not isinstance(value, Psifas):
            return super(Dynamic, self).mapping(value)
        return value
                
class Switch(MappingSwitch):
    r"""
    According to the first value, decide how to parse the rest of the buffer.
    
        >>> MY_FIXED_SWITCH = Switch(Byte(),
        ...                    {'>': 'BIG',
        ...                    '<': 'LITTLE'},
        ...                    default = 'OTHER')
        >>> MY_FIXED_SWITCH.parse('>')
        'BIG'
        >>> MY_FIXED_SWITCH.parse('?')
        'OTHER'
        >>> MY_FIXED_SWITCH.build('LITTLE') # when the values are constant, reversing is possible
        '<'

    Here we can see how to use the Switch for actually parsing the rest of the buffer differently.

        >>> MY_SWITCH = Struct('decider', Byte(),
        ...                    'value', Switch(This.decider,
        ...                                    {'>': UBInt(4),
        ...                                     '<': ULInt(4)},
        ...                                     default = Segment(4)))
        >>> parsed_container = MY_SWITCH.parse('>\x00\x00\x00\x01')
        >>> parsed_container
        Container(...)
        >>> parsed_container.value
        1
        >>> parsed_container = MY_SWITCH.parse('<\x02\x00\x00\x00')
        >>> parsed_container
        Container(...)
        >>> parsed_container.value
        2
        >>> parsed_container = MY_SWITCH.parse('Q\x03\x00\x00\x00')
        >>> parsed_container
        Container(...)
        >>> parsed_container.value
        '\x03\x00\x00\x00'
        >>> MY_SWITCH.build(Container(decider = '>', value = 7))
        '>\x00\x00\x00\x07'
        >>> MY_SWITCH.build(Container(decider = '?', value = 'abcd'))
        '?abcd'
    """
    def __init__(self, switch_psifas, mapping_dict = None, default = Top, **mapping_extension):
        if mapping_dict is None:
            mapping_dict = dict()
        elif not isinstance(switch_psifas, Psifas):
            switch_psifas = Constant(switch_psifas) # huh? Constant switch-field?
        
        super(Switch, self).__init__(switch_psifas)

        self.mapping_dict = dict(mapping_dict, **mapping_extension)
        for (key, value) in self.mapping_dict.items():
            if not isinstance(value, Psifas):
                self.mapping_dict[key] = Constant(value)
        
        self.default = default if ((default is Top) or isinstance(default, Psifas)) else Constant(default)
    
    def mapping(self, switch_value):
        return  self.mapping_dict.get(switch_value,
                                     self.default if not is_abstract(switch_value)
                                     else super(Switch, self).mapping(switch_value))

    def reverse_mapping_abstract(self, solution):
        if any(not isinstance(psifas, Constant) for psifas in self.mapping_dict.itervalues()):
            return Top
        if isinstance(self.default, Constant) and (solution == self.default.value):
            return Top
        result = Top
        for key, psifas in self.mapping_dict.iteritems():
            if psifas.value == solution:
                if result is not Top:
                    # 2 maps match
                    return Top
                result = key
        return result

    def _more_sub_psifases(self):
        return self.mapping_dict.itervalues()

class _load_mapping_dict_metaclass(type):
    """
    Do Not Panic.
    This feature simply calls load_mapping_dict automatically after
    sub-classes of Enum are created.
    """
    def __new__(mcs, name, bases, namespace):
        enum_class = type.__new__(mcs, name, bases, namespace)
        enum_class.load_mapping_dict((key, value) for (key, value) in namespace.iteritems() if key.isupper() and not key.startswith('_'))
        return enum_class

class Enum(MappingSwitch):
    r"""
    Inherit from this class inorder to create your own enums.
    For example:

        >>> class MyEnum(Enum):
        ...     ONE = 1
        ...     TWO = 2
        ...     THREE = 3
        ...     # when written in lowercase or with non alphanum chars, 
        ...     # the constant must be put inside the 'constants' dictionary:
        ...     constants = {'the number four': 4}
        >>> MY_STRUCT = Struct('a', MyEnum(UBInt(1)),
        ...                    'b', MyEnum(UBInt(4)))
        >>> parsed_container = MY_STRUCT.parse('\x01\x00\x00\x00\x03')
        >>> parsed_container
        Container(...)
        >>> parsed_container.a, parsed_container.b
        ('ONE', 'THREE')
        >>> MY_STRUCT.build(Container(a = 'the number four', b = 'TWO'))
        '\x04\x00\x00\x00\x02'
    """
    __metaclass__ = _load_mapping_dict_metaclass

    constants = {}

    def __init__(self, switch_psifas):
        super(Enum, self).__init__(UniqueField('enum', switch_psifas))

    @classmethod
    def load_mapping_dict(cls, constants):
        """
        This function should also be called if enum_dict is updated after
        the class creation.
        """
        cls.constants = cls.constants.copy() # don't change he original dictionary - allows inheritence
        cls.constants.update(constants)
        
        cls.mapping_dict = dict((value, Constant(key)) for (key, value) in cls.constants.iteritems())
        
    def mapping(self, switch_value):
        if not is_abstract(switch_value):
            return self.mapping_dict[switch_value]
        return self.mapping_dict.get(switch_value, PlaceHolder())

    def reverse_mapping(self, solution):
        return self.constants.get(solution, Top)
    
    def _more_sub_psifases(self):
        return self.mapping_dict.itervalues()

