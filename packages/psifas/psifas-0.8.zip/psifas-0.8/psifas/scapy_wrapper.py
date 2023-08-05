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

r"""

Example: Parser and Builder of cap files (you must have the scapy package for this test to work).

The pcap file is from:
http://wiki.wireshark.org/SampleCaptures

    >>> import scapy.all
    >>> from copy import deepcopy
    >>> pcap_file = 'd4c3b2a1020004000000000000000000ffff000001000000885eb3410dd804003a0100003a010000ffffffffffff000b8201fc4208004500012ca8360000fa11178b00000000ffffffff004400430118591f0101060000003d1d00000000000000000000' \
    ...             '00000000000000000000000b8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '000000000000000000000000000000000000638253633501013d0701000b8201fc4232040000000037040103062aff00000000000000885eb34134d904005601000056010000000b8201fc42000874adf19b0800450001480445000080110000c0a80001' \
    ...             'c0a8000a00430044013422330201060000003d1d0000000000000000c0a8000ac0a8000100000000000b8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501020104ffffff003a04000007083b0400000c4e330400000e103604c0a80001ff0000000000000000000000000000' \
    ...             '000000000000000000000000885eb3419ce905003a0100003a010000ffffffffffff000b8201fc4208004500012ca8370000fa11178a00000000ffffffff0044004301189fbd0101060000003d1e0000000000000000000000000000000000000000000b' \
    ...             '8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '000000000000638253633501033d0701000b8201fc423204c0a8000a3604c0a8000137040103062aff00885eb341d6ea05005601000056010000000b8201fc42000874adf19b0800450001480446000080110000c0a80001c0a8000a004300440134dfdb' \
    ...             '0201060000003d1e0000000000000000c0a8000a0000000000000000000b8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
    ...             '000000000000000000000000000000000000000000000000000000000000000000000000638253633501053a04000007083b0400000c4e330400000e103604c0a800010104ffffff00ff0000000000000000000000000000000000000000000000000000'
    >>> pcap_file = pcap_file.decode('hex')
    >>> results = []
    >>> for scapy_class in (Scapy, ScapyStruct): 
    ...     PCAP_ETHER = Struct('pcap_header', Struct('magic_number', UBInt(4),
    ...                                               'endian', Switch(This.magic_number,
    ...                                                                {0xa1b2c3d4: 'BIG',
    ...                                                                 0xd4c3b2a1: 'LITTLE'}),
    ...                                               '.endian_unsigned_long', Switch(This.endian,
    ...                                                                               {'BIG': Constant(UBInt(4)),
    ...                                                                                'LITTLE': Constant(ULInt(4))}),
    ...                                               '.endian_unsigned_short', Switch(This.endian,
    ...                                                                                {'BIG': Constant(UBInt(2)),
    ...                                                                                 'LITTLE': Constant(ULInt(2))}),
    ...                                               '.endian_signed_long', Switch(This.endian,
    ...                                                                             {'BIG': Constant(SBInt(4)),
    ...                                                                              'LITTLE': Constant(SLInt(4))}),
    ...                                               'version_major', Dynamic(This/'.endian_unsigned_short'),
    ...                                               'version_minor', Dynamic(This/'.endian_unsigned_short'),
    ...                                               'thiszone', Dynamic(This/'.endian_signed_long'),
    ...                                               'sigfigs', Dynamic(This/'.endian_unsigned_long'),
    ...                                               'snaplen', Dynamic(This/'.endian_unsigned_long'),
    ...                                               'network', Dynamic(This/'.endian_unsigned_long'), Constant(1)),
    ...                         'packets', RepeatUntilTerm(Struct('ts_sec', Dynamic(This/'.../pcap_header/.endian_unsigned_long'),
    ...                                                           'ts_usec', Dynamic(This/'.../pcap_header/.endian_unsigned_long'),
    ...                                                           'incl_len', Dynamic(This/'.../pcap_header/.endian_unsigned_long'),
    ...                                                           'orig_len', Dynamic(This/'.../pcap_header/.endian_unsigned_long'),
    ...                                                           'packet', scapy_class(scapy.all.Ether).on(Segment(This.incl_len)),
    ...                                                           ),
    ...                                                    IsEOF()
    ...                                                    ))
    ...     dhcp_packets = PCAP_ETHER.parse(pcap_file)
    ...     results.append(dhcp_packets)
    ...     assert PCAP_ETHER.build(deepcopy(dhcp_packets)) == pcap_file # rebuiding and validating that the result is identical to the original content of dhcp.pcap
    >>> print results[0].pcap_header
    Container(...)
    >>> print results[0].packets[0] # example packet
    Container(...)
    >>> print results[1].pcap_header
    Container(...)
    >>> print results[1].packets[0] # example packet
    Container(...)
"""

try:
    import scapy.all as _scapy
except ImportError:
    raise ImportWarning("psifas will not support scapy wrappers because scapy is not installed")

from base import Psifas, Field, Constant, Payload, UniqueField, PayloadlessPlaceHolder
from payload_constraint import SetPayloadConstraint
from constraint import Constraint, SetValueByValueConstraint
from utils import pairwise

from datatypes.container import Container
from datatypes.sparse import SparseString
from datatypes.abstract import Top

from itertools import count
from functools import partial
from copy import deepcopy

import re as _re

_layer_field_syntax = _re.compile(r"(layer[1-9]\d*|layer[1-9]\d*_type)$")

class _ScapyPsifas(Psifas):
    class BuildLayersConstraint(Constraint):
        def _build_layers(self, source_location, layers_no_range = None):
            if layers_no_range is None:
                layers_no_range = count(1)
            layer_objects = []
            for layer_no in layers_no_range:
                if not source_location.context('layer%d_type' % (layer_no,)).get_is_concrete():
                    return None
                layer_class = source_location.context('layer%d_type' % (layer_no,)).get_value()
                if not isinstance(layer_class, type) or not issubclass(layer_class, _scapy.BasePacket):
                    return None
                if layer_class is _scapy.NoPayload:
                    break
                layer_objects.append(layer_class())
                if layer_class is _scapy.Raw:
                    break
            if len(layer_objects) == 0:
                return None
            return layer_objects
            
        
    class SetDissectorConstraint(BuildLayersConstraint):
        def _run(self, target_location, source_location):
            if not source_location.context('dissector_layers_no').get_is_concrete():
                return
            dissector_layers_no = source_location.context('dissector_layers_no').get_value()
            
            layer_objects = self._build_layers(source_location, xrange(1, dissector_layers_no + 1))
            if layer_objects is None:
                return
            for underlayer, upperlayer in pairwise(layer_objects):
                upperlayer.underlayer = underlayer
                underlayer.upperlayer = upperlayer
            target_location.context().set_value(layer_objects[0])

    class SetLayersTypesByDissectorConstraint(Constraint):
        def _run(self, target_location, source_location):
            if not target_location.context('dissector_layers_no').get_is_concrete():
                return
            dissector_layers_no = target_location.context('dissector_layers_no').get_value()

            if not source_location.context().get_is_concrete():
                return
            dissector_layer = source_location.context().get_value()
            for layer_no in xrange(1, dissector_layers_no):
                if dissector_layer is None:
                    break
                target_location.context('layer%d_type' % (layer_no,)).set_value(dissector_layer.__class__)
                
                if isinstance(dissector_layer, _scapy.Raw) or isinstance(dissector_layer, _scapy.NoPayload):
                    break
                dissector_layer = getattr(dissector_layer, 'upperlayer', None)

    class SetLayersFieldsByContainersConstraint(BuildLayersConstraint):
        def _run(self, location):
            layer_objects = self._build_layers(location)
            if layer_objects is None:
                return
            for layer_no, layer_object in enumerate(layer_objects):
                layer_container = location.context('layer%d' % (layer_no + 1,)).get_value()
                if not isinstance(layer_container, Container):
                    continue
    
                for field_name in set(layer_object.default_fields.keys() + layer_object.overloaded_fields.keys() + layer_object.fields.keys()):
                    location.context('layer%d/%s' % (layer_no + 1, field_name)).set_value(getattr(layer_container, field_name, Top))
                    field_value = location.context('packet_context/layer%d/%s' % (layer_no + 1, field_name)).value

    class SetLayersContainersByFieldsConstraint(BuildLayersConstraint):
        def _run(self, location):
            layer_objects = self._build_layers(location)
            if layer_objects is None:
                return
            
            for layer_no, layer_object in enumerate(layer_objects):
                layer_container = Container()
                for field_name in set(layer_object.default_fields.keys() + layer_object.overloaded_fields.keys() + layer_object.fields.keys()):
                    setattr(layer_container, field_name, location.context('layer%d/%s' % (layer_no + 1, field_name)).get_value())
            
                location.context('layer%d' % (layer_no + 1,)).set_value(layer_container)

    class SetScapyPacketByLayersFields(BuildLayersConstraint):
        def _run(self, target_location, source_location):
            layer_objects = self._build_layers(source_location)
            if layer_objects is None:
                return
            
            for layer_no, layer_object in enumerate(layer_objects):
                for field_name in set(layer_object.default_fields.keys() + layer_object.overloaded_fields.keys() + layer_object.fields.keys()):
                    if not source_location.context('layer%d/%s' % (layer_no + 1, field_name)).get_is_concrete():
                        return
                    layer_object.setfieldval(field_name, source_location.context('layer%d/%s' % (layer_no + 1, field_name)).get_value())
            for underlayer, upperlayer in pairwise(layer_objects):
                underlayer.add_payload(upperlayer)
            target_location.context().set_value(layer_objects[0])

    class SetLayersByScapyPacket(Constraint):
        def _run(self, target_location, source_location):
            if not source_location.context().get_is_concrete():
                return
            scapy_layer = source_location.context().get_value()
            
            for layer_no in count(1):
                # put the scapy-layer in the layer-contexts
                target_location.context('layer%d_type' % (layer_no,)).set_value(scapy_layer.__class__)
                # FEATURE: is there a more efficient way to evaluate the final values of all the fields?
                layer_fields = scapy_layer.__class__(str(scapy_layer)).fields
                for field_name, value in layer_fields.iteritems():
                    target_location.context('layer%d/%s' % (layer_no, field_name)).set_value(value)
                if isinstance(scapy_layer, _scapy.Raw) or isinstance(scapy_layer, _scapy.NoPayload):
                    break
                scapy_layer = scapy_layer.payload

    class SetGlobalContainerByLayersConstraint(Constraint):
        def _run(self, target_location, source_location):
            global_container = Container()
            for layer_no in count(1):
                layer_container = source_location.context('layer%d' % (layer_no,)).get_value()
                setattr(global_container, 'layer%d' % (layer_no,), layer_container)

                if not source_location.context('layer%d_type' % (layer_no,)).get_is_concrete():
                    break
    
                layer_type = source_location.context('layer%d_type' % (layer_no,)).get_value()
                setattr(global_container, 'layer%d_type' % (layer_no,), layer_type)
            target_location.context().set_value(global_container)

    class SetLayersByGlobalContainerConstraint(Constraint):
        def _run(self, target_location, source_location):
            global_container = source_location.context().get_value()
            if not isinstance(global_container, Container):
                return
            for attr, value in global_container.iter_fields():
                if _layer_field_syntax.match(attr) is None:
                    continue
                target_location.context(attr).set_value(value)

    class DissectPayloadConstraint(Constraint):
        def do_dissect_payload(self, underlayer, s):
            if s and hasattr(underlayer, 'upperlayer'):
                upperlayer = underlayer.upperlayer
                try:
                    upperlayer.dissect(s)
                    upperlayer.dissection_done(upperlayer)
                except:
                    upperlayer = _scapy.Raw(s, _internal = 1, _underlayer = underlayer)
                underlayer.add_payload(upperlayer)
        
        def _run(self, target_location, dissector_location, payload_location):
            if not dissector_location.context().get_is_concrete():
                return
            scapy_dissector = dissector_location.context().get_value()

            if not payload_location.payload_context().get_is_concrete():
                return
            payload = payload_location.payload_context().get_value()

            new_scapy_packet = deepcopy(scapy_dissector)

            layer = new_scapy_packet
            while getattr(layer, 'upperlayer', None) is not None:
                layer.do_dissect_payload = partial(self.do_dissect_payload, layer)
                layer = layer.upperlayer
            new_scapy_packet.dissect(payload)
            target_location.context().set_value(new_scapy_packet.copy())

    class SetPayloadByPacketConstraint(Constraint):
        def _run(self, target_location, source_location):
            if not source_location.context().get_is_concrete():
                return
            packet = source_location.context().get_value()
            if not isinstance(packet, _scapy.Packet):
                return
            target_location.payload_context().set_value(str(packet))
                
    def __init__(self, first_psifas, *other_psifases):
        all_psifases = (first_psifas,) + other_psifases
        layers_fields = [Field('layer%d_type' % (layer_index + 1,), layer_psifas) for layer_index, layer_psifas in enumerate(all_psifases)]
        layers_fields.append(Field('dissector_layers_no', Constant(len(all_psifases))))
        # TODO: sure about the following NoPayload?
        layers_fields.append(Field('.scapy_payload', Payload()))
        
        super(_ScapyPsifas, self).__init__(UniqueField('.scapy_dissector', PayloadlessPlaceHolder()),
                                           Field('.scapy_packet', PayloadlessPlaceHolder()),
                                           Field('.scapy_struct', Constant(Container())),
                                           *layers_fields)


    def _register_private_constraints(self, location):
        location.engine().constraints |= (SetPayloadConstraint(location, SparseString()),
                                          self.SetDissectorConstraint(location[0], location),
                                          self.SetLayersTypesByDissectorConstraint(location, location[0]),
                                          self.SetLayersFieldsByContainersConstraint(location),
                                          self.SetLayersContainersByFieldsConstraint(location),
                                          self.SetScapyPacketByLayersFields(location[1], location),
                                          self.SetLayersByScapyPacket(location, location[1]),
                                          self.SetGlobalContainerByLayersConstraint(location[2], location),
                                          self.SetLayersByGlobalContainerConstraint(location, location[2]),
                                          self.DissectPayloadConstraint(location[1], location[0], location[-1]),
                                          self.SetPayloadByPacketConstraint(location[-1], location[1]))
                                          
                                          

                                          
class Scapy(_ScapyPsifas):
    def _register_private_constraints(self, location):
        super(Scapy, self)._register_private_constraints(location)
        location.engine().constraints |= (SetValueByValueConstraint(location, location[1]),
                                          SetValueByValueConstraint(location[1], location))

class ScapyStruct(_ScapyPsifas):
    def _register_private_constraints(self, location):
        super(ScapyStruct, self)._register_private_constraints(location)
        location.engine().constraints |= (SetValueByValueConstraint(location, location[2]),
                                          SetValueByValueConstraint(location[2], location))
