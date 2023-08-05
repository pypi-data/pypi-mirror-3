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

from datatypes.deque import deque

from collections import defaultdict
from functools import wraps
import thread
from itertools import izip


class RecursionLockException(AssertionError):
    """
    This error is an assertion error - not just an error of usage.
    """
    pass

_recursion_lock_sets = defaultdict(deque)

def recursion_lock(replace_func, exclude = ()):
    """
    replace_func - the function to use in case of recursion
    exclude - a list\tuple of the names & indexes of the args to ignore when checking for recursion.
    for example, see the pretty_str func, in whchi the 'nesting' variable (given in the kws or
    arg #1) is increased in every sub-call, and by ignoring it we can still find out if a recursive
    call happend.
    """
    def decorator(func):
        dummy = object()
        @wraps(func)
        def new_func(*args, **kws):
            recursion_lock_set = _recursion_lock_sets[thread.get_ident()]
            if len(exclude) == 0:
                key_args = args
                key_kws = kws
            else:
                key_args = tuple(arg for ind, arg in enumerate(args) if ind not in exclude)
                key_kws = kws.copy()
                for name in exclude:
                    key_kws.pop(name, None)
            for (rec_func, rec_args, rec_kws) in recursion_lock_set:
                if (func is rec_func) and \
                   (len(key_args) == len(rec_args)) and \
                   all(key_arg is rec_arg for (key_arg, rec_arg) in izip(key_args, rec_args)) and \
                   (len(key_kws) == len(rec_kws)) and \
                   all((value is rec_kws.get(name, dummy)) for (name, value) in key_kws.iteritems()):
                    return replace_func(*args, **kws)
            recursion_key = (func, key_args, key_kws)
            recursion_lock_set.append(recursion_key)
            try:
                rle = None
                return func(*args, **kws)
            except RecursionLockException, rle:
                raise
            finally:
                if rle is None:
                    try:
                        if recursion_lock_set.pop() is not recursion_key:
                            raise RecursionLockException("the recursion-lock set top key is not the expected value")
                    except IndexError:
                        raise RecursionLockException("the recursion-lock set top key does not exists")
                        
                    if len(recursion_lock_set) == 0:
                        if _recursion_lock_sets.pop(thread.get_ident(), None) is not recursion_lock_set:
                            raise RecursionLockException("the recursion-lock set was misused and is not in the set of all recursion-lock sets")
        return new_func
    return decorator
