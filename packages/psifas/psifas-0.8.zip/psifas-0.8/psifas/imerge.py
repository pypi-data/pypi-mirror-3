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

from psifas_exceptions import MergeException
from scapy_packet import ScapyPacket, ScapyNoPayload

import datatypes
import datatypes.abstract
from datatypes.dummy import MetaSequence, MetaBytes, DummyPayload, optimized_list, optimized_tuple

from itertools import izip, combinations
import numbers
from sys import float_info

def imerge_sequence_sequence(a, b):
    if len(a) != len(b):
        return MergeException("Sequences have different lengths", a, b)
    new_a = optimized_list([datatypes.abstract.Top]) * len(a)
    
    total_merge_flag = False
    for index, (sub_a, sub_b) in enumerate(izip(a, b)):
        new_a[index], merge_flag = imerge_unwrapped(sub_a, sub_b)
        if merge_flag:
            total_merge_flag = True
    return new_a, total_merge_flag

def imerge_sequence(a, b):
    if isinstance(b, MetaSequence) and not isinstance(b, MetaBytes):
        return imerge_sequence_sequence(a, b)
    raise MergeException("Cannot merge sequence with this type of object", a, b)

def imerge_metabytes(a, b):
    if isinstance(b, MetaBytes):
        # string with same string?
        if a == b:
            return a, False
        else:
            raise MergeException("Cannot merge different strings", a, b)
    raise MergeException("Cannot merge bytes with this type of object", a, b)

def imerge_number(a, b):
    if isinstance(b, numbers.Number) and (isinstance(a, float) or isinstance(b, float)):
        if abs(a - b) < float_info.epsilon * 10:
            return a, False
        raise MergeException("Different numbers: %r, %r" % (a, b))
    raise MergeException("Cannot merge number with this type of object", a, b)

def _builtins_imerge(a, b):
    """
    How merge works for types that does not have the imerge function
    """
    if isinstance(a, MetaBytes):
        return imerge_metabytes(a, b)

    if isinstance(a, MetaSequence):
        # list imerge
        return imerge_sequence(a, b)
            
    if isinstance(a, numbers.Number):
        return imerge_number(a, b)

    if isinstance(a, ScapyPacket) and isinstance(b, ScapyPacket) and bytes(a) == bytes(b):
        a_layer = a
        b_layer = b
        while not isinstance(a_layer, ScapyNoPayload) or not isinstance(b_layer, ScapyNoPayload):
            if a_layer.__class__ is not b_layer.__class__:
                break
            a_layer = a_layer.payload
            b_layer = b_layer.payload
        else:
            return a, False

    raise MergeException('different concrete values or abstract values that cannot be merged', a, b)

def imerge_unwrapped(a, b):
    """
    Tries to inclusive-merge 'a' with 'b'.
    Returns 2 values:
    - the merged value (if it was inclusive, it will be the object 'a')
    - a boolean whether the merge did any changes
    """
    if (a is b) or (a == b):
        return a, False
    if isinstance(b, datatypes.abstract.TopClass) and not isinstance(a, datatypes.abstract.TopClass):
        # A merge of any value with TopClass will return the samve value.
        # If both values are TopClass, their imerge will be called.
        return a, False
    imerge_func = _builtins_imerge_common.get((type(a), type(b)), None)
    if imerge_func is not None:
        return imerge_func(a, b)
    imerge_func = getattr(a, 'imerge', None)
    if imerge_func is not None:
        return imerge_func(b)
    imerge_func = getattr(b, 'rimerge', None)
    if imerge_func is not None:
        return imerge_func(a)
    return _builtins_imerge(a, b)

def imerge(a, b):
    try:
        return imerge_unwrapped(a, b)
    except MergeException, e:
        raise MergeException("inner merge failure: %s" % (e.args[0],), a, b, *e.args[1:])

_builtins_imerge_common = dict([(comb, imerge_sequence_sequence) for comb in combinations((list, tuple, optimized_list, optimized_tuple), 2)] +
                               [(comb, imerge_metabytes) for comb in combinations((bytes, DummyPayload), 2)])
