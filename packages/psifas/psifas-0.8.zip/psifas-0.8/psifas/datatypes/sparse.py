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

from abstract import Abstract, Top, is_abstract, CharAbstraction, StringAbstraction, SequenceAbstraction
from dummy import MetaSequence, MetaBytes, MetaList, sequence_sum, optimized_list, optimized_tuple, sortedlist, DummyPayload

from ..psifas_exceptions import MergeException
from ..recursion_lock import recursion_lock

from .. import imerge
import numbers
import heapq
from copy import deepcopy

from sys import maxint


from itertools import izip, chain, repeat

class SectorCollection(object):
    def __init__(self, sectors = ()):
        # assumes that the sectors do not overlap and are not empty
        super(SectorCollection, self).__init__()
        if len(sectors) == 0:
            self.starts = sortedlist()
            self.ends = sortedlist()
        else:
            self.starts, self.ends = map(sortedlist, zip(*sectors))

    def __iter__(self):
        return izip(self.starts, self.ends)

    def iter_indices(self, limit = maxint):
        for (start, end) in izip(self.starts, self.ends):
            if start >= limit:
                break
            yield start, True
            if end > limit:
                yield limit, False
                break
            yield end, False
            
    def iter_joined_sectors(self, other, limit = maxint):
        my_iterator = self.iter_indices(limit)
        my_index, my_is_dirty = next(my_iterator, (None, False))
        
        other_iterator = other.iter_indices(limit)
        other_index, other_is_dirty = next(other_iterator, (None, False))

        my_is_dirty = other_is_dirty = False
        
        last_index = 0

        for (next_index, my_is_dirty_new, other_is_dirty_new) in heapq.merge(((index, is_dirty, None) for (index, is_dirty) in self.iter_indices(limit)),
                                                                             ((index, None, is_dirty) for (index, is_dirty) in other.iter_indices(limit))):
            if next_index > last_index:
                yield (last_index, next_index), (my_is_dirty, other_is_dirty)
                last_index = next_index
            if my_is_dirty_new is not None:
                my_is_dirty = my_is_dirty_new
            if other_is_dirty_new is not None:
                other_is_dirty = other_is_dirty_new
                
    def __len__(self):
        return len(self.starts)

    # in the following operations I assume the user does not create overlapping sectors

    def __getitem__(self, key):
        if isinstance(key, numbers.Number):
            return (self.starts[key], self.ends[key])
        return SectorCollection(zip(self.starts[key], self.ends[key]))

    def __delitem__(self, key):
        del self.starts[key]
        del self.ends[key]

    def __setitem__(self, key, value):
        if isinstance(key, numbers.Number):
            start, end = value
            self.starts[key] = start
            self.ends[key] = end
            return
        del self.starts[key]
        del self.ends[key]
        if len(value) == 0:
            return
        starts, ends = zip(*value)
        self.starts.update(starts)
        self.ends.update(ends)
    
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def bisect_right(self, offset):
        """
        The return value i is such that all e in self[:i] have e <= offset (smaller or contain the offset)
        and all e in a[i:] have e > offset (larger than offset).
        """
        return self.starts.bisect_right(offset)
    bisect = bisect_right

    def bisect_left(self, offset):
        """
        The return value i is such that all e in self[:i] have e < offset (smaller then offset)
        and all e in a[i:] have e >= offset (larger or contains the offset).
        """
        # this is weird but it works because the sectors end with a value that they don't contain
        return self.ends.bisect_right(offset)

    def is_cutting(self, (start, end)):
        return self.starts.bisect_left(end) - 1 >= self.ends.bisect_right(start)
    
    def __contains__(self, key):
        if isinstance(key, numbers.Number):
            # finds the right-most start-index that is smaller or equal to key
            sector_index = self.starts.bisect_right(key) - 1
            return (sector_index >= 0) and (key < self.ends[sector_index])
        try:
            key_start, key_end = key
        except ValueError:
            raise TypeError("key is not a 2-values tuple")
        return self.starts.bisect_right(key_start) - 1 == self.ends.bisect_left(key_end)

    def add(self, key):
        if isinstance(key, numbers.Number):
            key_start = key
            key_end = key + 1
        else:
            try:
                key_start, key_end = key
            except ValueError:
                raise TypeError("key is not a 2-values tuple")
            if key_start >= key_end:
                return self
        start_sector_index = self.starts.bisect_right(key_start) - 1
        if (start_sector_index >= 0) and (key_start <= self.ends[start_sector_index]):
            # key_start is inside the sector
            key_start = self.starts[start_sector_index]
        else:
            # key_start is not inside the sector
            start_sector_index += 1

        end_sector_index = self.ends.bisect_left(key_end)
        if (end_sector_index < len(self.starts)) and (self.starts[end_sector_index] <= key_end):
            key_end = self.ends[end_sector_index]
        else:
            end_sector_index -= 1

        del self.starts[start_sector_index:end_sector_index+1]
        del self.ends[start_sector_index:end_sector_index+1]

        self.starts.add(key_start)
        self.ends.add(key_end)

        return self

    def sub(self, key):
        if isinstance(key, numbers.Number):
            key_start = key
            key_end = key + 1
        else:
            try:
                key_start, key_end = key
            except ValueError:
                raise TypeError("key is not a 2-values tuple")
            if key_start >= key_end:
                return self

        new_starts = []
        new_ends = []
        
        start_sector_index = self.starts.bisect_right(key_start) - 1
        if (start_sector_index >= 0) and (key_start <= self.ends[start_sector_index]):
            # key_start is inside the sector
            start_sector_start = self.starts[start_sector_index]
            if key_start != start_sector_start:
                new_starts.append(start_sector_start)
                new_ends.append(key_start)
        else:
            # key_start is not inside the sector
            start_sector_index += 1

        end_sector_index = self.ends.bisect_left(key_end)
        if (end_sector_index < len(self.starts)) and (self.starts[end_sector_index] <= key_end):
            end_sector_end = self.ends[end_sector_index]
            if key_end != end_sector_end:
                new_ends.append(end_sector_end)
                new_starts.append(key_end)
        else:
            end_sector_index -= 1

        del self.starts[start_sector_index:end_sector_index+1]
        del self.ends[start_sector_index:end_sector_index+1]

        self.starts.update(new_starts)
        self.ends.update(new_ends)

        return self


class _SparseSequence(Abstract):
    default_element = Top
    _imerge_fixed_length_mergeable_type_wrapper = lambda x:x
    
    def __init__(self, value = (), min_length = 0, max_length = maxint, sectors = None):
        assert min_length <= max_length
        self.value = value[:max_length]
        self.min_length = min_length
        self.max_length = max_length
        # the sectors symbolize the "touched" areas - all the other sectors must
        # contain only default_element
        if sectors is None:
            self.sectors = SectorCollection([(0, len(self.value))] if len(self.value) > 0 else [])
        else:
            self.sectors = SectorCollection(sectors)
        self._clean()
        
    @classmethod
    def from_length(cls, length):
        return cls((), min_length = length, max_length = length)

    def length_range(self):
        return self.min_length, self.max_length

    def _clean(self):
        if len(self.value) > self.max_length:
            self.value = self.value[:self.max_length]
        if len(self.value) > 0 and self.value[-1] is self.default_element:
            for new_length in xrange(len(self.value) - 1, 0, -1):
                if self.value[new_length - 1] is not self.default_element:
                    break
            else:
                new_length = 0
            self.value = self.value[:new_length]
        self.sectors.sub((len(self.value), maxint))
        if self.max_length > maxint:
            self.max_length = maxint

    def is_all_touched(self):
        if (len(self.value) != self.min_length) or (self.min_length != self.max_length):
            return False
        if len(self.sectors) != 1 or self.sectors[0][0] > 0 or self.sectors[-1][1] < self.min_length:
            return False
        return True
    
    def is_abstract(self, next_args):
        if not self.is_all_touched():
            return True
        next_args.append(self.value)
        return False
        
    def value_at(self, index):
        """
        returns the value at the given index when ignoring the min_length, max_length limits
        """
        if len(self.value) > index:
            return self.value[index]
        return self.default_element

    def __repr__(self):
        if self.max_length == self.min_length:
            return '%s(length = %d, value = %r + (%r, ...))' % (self.__class__.__name__,
                                                                self.min_length,
                                                                self.value,
                                                                self.default_element)
        return '%s(min_length = %d, max_length = %d, value = %r + (%r, ...))' % (self.__class__.__name__,
                                                                                 self.min_length,
                                                                                 self.max_length,
                                                                                 self.value,
                                                                                 self.default_element)
        
    def __getitem__(self, key):
        if not isinstance(key, slice):
            assert isinstance(key, numbers.Number)
            if key < 0:
                if self.min_length != self.max_length:
                    return self.default_element
                key = self.max_length + key
            if (key < 0) or (key >= self.min_length):
                raise IndexError("index may be out of range")
            if key < self.min_length:
                return self.value_at(key)
            return self.default_element # it may also be out of range..
        # key is a slice
        if self.min_length != self.max_length:
            starts, stops, steps = zip(key.indices(self.min_length),
                                       key.indices(self.min_length + 1),
                                       key.indices(min(self.max_length, maxint)),
                                       key.indices(min(self.max_length - 1, maxint)))
        else:
            starts, stops, steps = zip(key.indices(self.min_length))

        if len(set(starts)) > 1 or starts[0] == -1:
            # we don't know where the slice begins..
            slice_value = ()
            slice_sectors = ()
        else:
            # self.min_length is not supposed to be a very large number (over physible buffers used in the psifas)
            # therefore min_start (which equals max_start) is not a very large either.
            start = starts[0]
            step = steps[0]
            required_length = max(start + 1, max(stops))
            value_sliced = optimized_tuple(self.value[:required_length])
            if step < 0:
                # the values of "self.value" will come at the end of the slice.
                completed_value = value_sliced + (optimized_tuple((self.default_element,)) * (required_length - len(value_sliced)))

                slice_value = completed_value[start::step]
                slice_sectors = self.sectors[:self.sectors.bisect_right(start)]
                slice_sectors.sub((start + 1, maxint))
                slice_sectors = [((sector_end - required_length) / step,
                                  (sector_start - required_length) / step)
                                 for (sector_start, sector_end) in slice_sectors
                                 if (sector_end - sector_start >= abs(step))]
            else:
                slice_value = value_sliced[start::step]
                slice_sectors = self.sectors[self.sectors.bisect_left(start):]
                slice_sectors.sub((None, start))
                slice_sectors = [((sector_start - start) / step, (sector_end - start) / step)
                                 for (sector_start, sector_end) in slice_sectors
                                 if (sector_end - sector_start >= step)]

        slice_lengths = [(max(0, (stop - start + step - (1 if step > 0 else -1)) / step) if (start != -1) else 0)
                         for (start, stop, step) in zip(starts, stops, steps)]
        res = self.__class__(slice_value,
                             min_length = min(slice_lengths),
                             max_length = max(slice_lengths),
                             sectors = slice_sectors)
        if not is_abstract(res):
            return res.value
        return res
    
    def listify(self):
        """
        Called whenever we want to make sure that the inner is a list.
        """
        if not isinstance(self.value, MetaList):
            self.value = optimized_list(self.value)

    def _setitem(self, key, value = (), is_delitem = False):
        if not isinstance(key, slice):
            assert isinstance(key, numbers.Number)
            if key < 0:
                key = self.min_length + key
                if key < 0:
                    raise IndexError("sparse list assignment index may be out of range")
                if self.min_length != self.max_length:
                    self.listify()
                    del self.value[key:]
                    self.sectors.sub((key, maxint))
                    self._clean()
                    return
            elif key >= self.min_length:
                raise IndexError("sparse list assignemnt index may be out of range")
            self.listify()
            if len(self.value) <= key:
                # does not affect "touched" sectors:
                self.value += optimized_list((self.default_element,)) * (key + 1 - len(self.value))
            self.value[key] = value
            self.sectors.add(key)
            self._clean()
            return
        # key is a slice
        if not isinstance(value, (MetaBytes, MetaSequence)):
            value = optimized_tuple(value)

        if self.min_length != self.max_length:
            starts, stops, steps = zip(key.indices(self.min_length),
                                       key.indices(self.min_length + 1),
                                       key.indices(min(self.max_length, maxint)),
                                       key.indices(min(self.max_length - 1, maxint)))
        else:
            starts, stops, steps = zip(key.indices(self.min_length))

        slice_lengths = [(max(0, (stop - start + step - (1 if step > 0 else -1)) / step) if (start != -1) else 0)
                         for (start, stop, step) in zip(starts, stops, steps)]

        assert len(set(steps)) == 1
        step = steps[0]

        if step != 1:
            if len(value) != min(slice_lengths):
                raise ValueError("attempt to assign sequence of size %d to extended slice of possible size %d" % (len(value), min(slice_lengths)))
            if len(value) != max(slice_lengths):
                raise ValueError("attempt to assign sequence of size %d to extended slice of possible size %d" % (len(value), max(slice_lengths)))
        
        # we don't need to extend self.value much over the new-slice - because it's going to be deleted anyway.
        required_length = min(self.max_length, max(max(starts), max(starts) + ((max(slice_lengths) - 1) * step)) + 1)
        self.listify()
        # does not affect "touched" sectors:
        self.value += optimized_list((self.default_element,)) * (required_length - len(self.value))
        try:
            if max(starts) == -1:
                # all the starts are invalid
                if len(value) > 0:
                    raise ValueError("attempt to assign sequence of size %d to extended slice of size 0" % (len(value),))
            elif (len(set(starts)) > 1) or (len(set(stops)) > 1):
                # when there's -1 in the stops, min(stops) + 1 == 0
                slice_offset = min(min(s for s in starts if s != -1), min(stops) + 1)
                del self.value[slice_offset:]
                self.sectors.sub((slice_offset, maxint))
            else:
                start = starts[0]
                stop = stops[0]
                if stop == -1:
                    stop = None
                slice_length = slice_lengths[0]
                if step > 0:
                    change_start = start
                    change_end = stop if stop is not None else len(self.value)
                else:
                    change_start = (stop + 1) if stop is not None else 0
                    change_end = start + 1
                if is_delitem:                    
                    del self.value[start:stop:step]
                else:
                    self.value[start:stop:step] = value
                # now we can delete the sectors
                if self.sectors.is_cutting((change_start, change_end)):
                    # the change-area has changed its length
                    self.sectors.sub((change_start, change_end))
                shift = slice_length - len(value)
                if shift != 0:
                    shifted_sectors = [(sector_start - shift, sector_end - shift) for (sector_start, sector_end) in
                                       self.sectors[self.sectors.bisect_left(change_end):]]
                    self.sectors.sub((change_end, maxint))
                    if len(shifted_sectors) > 0:
                        self.sectors.add(shifted_sectors[0])
                        self.sectors[len(self.sectors):] = shifted_sectors[1:]
                self.sectors.add((change_start, change_end - slice_length + len(value)))
                    
            self.min_length = max(0, self.min_length - max(slice_lengths) + len(value))
            self.max_length = max(0, self.max_length - min(slice_lengths) + len(value))
        finally:
            self._clean()

    def __setitem__(self, key, value):
        return self._setitem(key, value)

    def __delitem__(self, key):
        if not isinstance(key, slice):
            if key != -1:
                key = slice(key, key + 1)
            else:
                key = slice(key, None)
        return self._setitem(key, is_delitem = True)

    def _is_variant_length_mergeable_type(self, other):
        raise NotImplementedError

    def _is_fixed_length_mergeable_type(self, other):
        raise NotImplementedError

    def imerge_variant_length_mergeable_type(self, other):
        if self.min_length > other.max_length:
            raise MergeException("Cannot merge %s with a shorter sparse sequence" % (self.__class__.__name__,), self, other)
        if self.max_length < other.min_length:
            raise MergeException("Cannot merge %s with a longer sparse sequence" % (self.__class__.__name__,), self, other)
        
        merges = optimized_list()
        
        change_flag = False
        
        if self.max_length > other.max_length:
            new_max_length = other.max_length
            change_flag = True
        else:
            new_max_length = self.max_length
        if self.min_length < other.min_length:
            new_min_length = other.min_length
            change_flag = True
        else:
            new_min_length = self.min_length
        
        repeat_end = max(len(self.value), len(other.value))
        
        if self.default_element is not other.default_element:
            # probably won't happen:
            merged_default, default_flag = imerge.imerge_unwrapped(deepcopy(self.default_element), other.default_element)
        else:
            default_flag = False
            merged_default = self.default_element

        merges = optimized_list([merged_default]) * repeat_end

        merge_sectors = SectorCollection()

        min_touch_index = maxint

        for (sector_start, sector_end), (my_is_dirty, other_is_dirty) in self.sectors.iter_joined_sectors(other.sectors, new_max_length):
            if my_is_dirty:
                if other_is_dirty:
                    inner_merge_failure = False
                    for index in xrange(sector_start, sector_end):
                        try:
                            merges[index], flag = imerge.imerge_unwrapped(self.value[index], other.value[index])
                        except MergeException:
                            if index < self.min_length:
                                # TODO: revert changes in previous merges?
                                raise
                            else:
                                # merges failed from this index..
                                inner_merge_failure = True
                                new_max_length = index
                                break
                        if flag:
                            change_flag = True
                    if inner_merge_failure:
                        break
                else:
                    merges[sector_start:sector_end] = self.value[sector_start:sector_end]
            elif other_is_dirty:
                merges[sector_start:sector_end] = other.value[sector_start:sector_end]
                min_touch_index = min(min_touch_index, sector_start)
            else:
                continue
            merge_sectors.add((sector_start, sector_end))
                    
        self.value = merges
        self.max_length = new_max_length
        self.min_length = new_min_length
        self.sectors = merge_sectors
        
        self._clean()

        if min_touch_index < len(self.value):
            change_flag = True
        
        if not is_abstract(self):
            return self.concrete(), True
        return self, change_flag

    def imerge_fixed_length_mergeable_type(self, other):
        """
        This function is not the full implementation of this imerge - it should be wrapped.
        """
        if self.min_length > len(other):
            raise MergeException("Cannot merge %s with a shorter sequence" % (self.__class__.__name__,), self, other)
        if self.max_length < len(other):
            raise MergeException("Cannot merge %s with a longer sequence" % (self.__class__.__name__,), self, other)
        # FEATURE: make more efficient without using zip that returns non-optimized sequences?
        if len(other) == 0:
            merges = []
        elif len(self.sectors) == 0:
            # more efficient
            merges = other
        else:
            merges = optimized_list()
            last_sector_end = 0
            for (sector_start, sector_end) in self.sectors:
                # assumes self.default_element can merge with the elements in other:
                merges.extend(other[last_sector_end:sector_start])
                sub_merges, flags = zip(*(imerge.imerge_unwrapped(my_element, other_element) for my_element, other_element
                                          in izip(self.value[sector_start:sector_end], other[sector_start:sector_end])))
                merges.extend(sub_merges)
                last_sector_end = sector_end
            merges.extend(other[last_sector_end:])
        return self._imerge_fixed_length_mergeable_type_wrapper(merges), True

    def rimerge(self, other):
        if not self._is_fixed_length_mergeable_type(other):
            raise MergeException("Cannot merge %s" % (other.__class__.__name__,), other, self)
        # rimerge_fixed_length_mergeable_type:
        if len(other) < self.min_length:
            raise MergeException("Cannot merge %s with a longer sparse sequence" % (other.__class__.__name__,), other, self)
        if len(other) > self.max_length:
            raise MergeException("Cannot merge %s with a shorter sparse sequence" % (other.__class__.__name__,), other, self)
        if len(other) == 0:
            merges = []
            flag = False
        else:
            merges = optimized_list()
            flag = False
            last_sector_end = 0
            for (sector_start, sector_end) in self.sectors:
                # assumes self.default_element can merge with the elements in other:
                merges.extend(other[last_sector_end:sector_start])
                sub_merges, sub_flags = zip(*(imerge.imerge_unwrapped(other_element, my_element) for other_element, my_element
                                              in izip(other[sector_start:sector_end], self.value[sector_start:sector_end])))
                if any(sub_flags):
                    flag = True
                merges.extend(sub_merges)
                last_sector_end = sector_end
            merges.extend(other[last_sector_end:])

        return self._imerge_fixed_length_mergeable_type_wrapper(merges), flag
        
    def imerge(self, other):
        # doesn't have to handle Tops - see imerge_unwrapped
        if self._is_fixed_length_mergeable_type(other):
            return self.imerge_fixed_length_mergeable_type(other)
        if self._is_variant_length_mergeable_type(other):
            return self.imerge_variant_length_mergeable_type(other)
        raise MergeException("Cannot merge %s" % (self.__class__.__name__,), self, other)

    def __add__(self, other):
        if self._is_fixed_length_mergeable_type(other):
            if len(other) == 0:
                return self.__class__(self.value,
                                      min_length = self.min_length,
                                      max_length = self.max_length)
            if self.min_length != self.max_length:
                # cannot get a more concrete value... I'm not going to try all the possible merges...
                return self.__class__(self.value[:self.min_length],
                                      min_length = self.min_length + len(other),
                                      max_length = self.max_length + len(other),
                                      sectors = self.sectors[:].sub((self.min_length, maxint)))
            return self.__class__(sequence_sum(sequence_sum(self.value,
                                                            optimized_tuple((self.default_element,)) * (self.min_length - len(self.value))),
                                               other),
                                  min_length = self.min_length + len(other),
                                  max_length = self.max_length + len(other),
                                  sectors = self.sectors[:].add((self.min_length, self.min_length + len(other))))
        if self._is_variant_length_mergeable_type(other):
            if 0 == other.min_length == other.max_length:
                return self.__class__(self.value,
                                      min_length = self.min_length,
                                      max_length = self.max_length,
                                      sectors = self.sectors[:])
            if self.min_length != self.max_length:
                # cannot get a more concrete value... I'm not going to try all the possible merges...
                return self.__class__(self.value[:self.min_length],
                                      min_length = self.min_length + other.min_length,
                                      max_length = self.max_length + other.max_length,
                                      sectors = self.sectors[:].sub((self.min_length, maxint)))
            if len(other.value) > 0:
                new_value = sequence_sum(sequence_sum(self.value,
                                                      optimized_tuple((self.default_element,)) * (self.min_length - len(self.value))),
                                         other.value)
            else:
                new_value = self.value
            return self.__class__(new_value,
                                  min_length = self.min_length + other.min_length,
                                  max_length = self.max_length + other.max_length,
                                  sectors = list(self.sectors) + [(sector_start + self.min_length, sector_end + self.min_length)
                                                                  for (sector_start, sector_end)
                                                                  in other.sectors])
        return NotImplemented
    
    def __radd__(self, other):
        if self._is_fixed_length_mergeable_type(other):
            return self.__class__(sequence_sum(other, self.value),
                                  min_length = len(other) + self.min_length,
                                  max_length = len(other) + self.max_length,
                                  sectors = SectorCollection([(sector_start + len(other), sector_end + len(other))
                                                              for (sector_start, sector_end)
                                                              in self.sectors]).add((0, len(other))))
        return NotImplemented

    def _concrete(self):
        raise NotImplementedError
#         if isinstance(self.value, MetaBytes):
#             return optimized_tuple(self.value)
#         return self.value

class SparseSequence(_SparseSequence):
    _imerge_fixed_length_mergeable_type_wrapper = optimized_tuple

    def _is_fixed_length_mergeable_type(self, other):
        return isinstance(other, MetaSequence) and not isinstance(other, MetaBytes)

    def _is_variant_length_mergeable_type(self, other):
        return isinstance(other, SparseSequence)

    def concrete(self):
        if not self.is_all_touched():
            return self
        if isinstance(self.value, MetaBytes):
            return optimized_tuple(self.value)
        return self.value

SequenceAbstraction.register(SparseSequence)    
        
class SparseString(_SparseSequence):
    default_element = CharAbstraction

    _imerge_fixed_length_mergeable_type_wrapper = b''.join

    def __init__(self, value = b'', min_length = 0, max_length = maxint, sectors = None):
        super(SparseString, self).__init__(value, min_length = min_length, max_length = max_length, sectors = sectors)
        self._validate_value_type(value, True)

    @classmethod
    def prefix(cls, payload):
        if isinstance(payload, MetaBytes):
            return cls(payload, min_length = 0, max_length = len(payload))
        elif isinstance(payload, SparseString):
            return cls(deepcopy(payload.value), min_length = 0, max_length = payload.max_length)
        raise TypeError("Cannot create prefix for type %s" % (type(payload),))

    def _is_fixed_length_mergeable_type(self, other):
        return isinstance(other, MetaBytes)

    def __radd__(self, other):
        if isinstance(other, DummyPayload):
            return other._read_all() + self
        return super(SparseString, self).__radd__(other)

    def _is_variant_length_mergeable_type(self, other):
        return isinstance(other, SparseString)
    
    def _validate_value_type(self, value, is_slice):
        """
        makes sure the value is mergeable with the default_element
        """
        try:
            if is_slice:
                if not isinstance(value, MetaBytes):
                    for v in value:
                        imerge.imerge_unwrapped(deepcopy(self.default_element), v)
            else:
                imerge.imerge_unwrapped(deepcopy(self.default_element), value)
        except MergeException, e:
            raise TypeError("Cannot set a slice of %s with this type of object" % (self.__class__.__name__,), self, value)

    def _concrete(self):
        return b''.join(self.value)
    
    def __setitem__(self, key, value):
        self._validate_value_type(value, isinstance(key, slice))
        return super(SparseString, self).__setitem__(key, value)
    
    def __getitem__(self, key):
        res = super(SparseString, self).__getitem__(key)
        if isinstance(key, slice) and isinstance(res, MetaSequence):
            return ''.join(res)
        return res

StringAbstraction.register(SparseString)
    
