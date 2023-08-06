#!/usr/bin/env python
"""
Sub-Package STDLIB of Package PLIB -- Python Standard Library Extensions
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains classes and functions which extend or
modify the Python standard library.

Note that, as with the PLIB.CLASSES sub-package, the ModuleProxy
class from the PLIB.UTILS sub-package is used to put the sub-modules
of this package in the package namespace, so that you can write,
for example,

    from plib.stdlib import abstractcontainer

instead of having to write

    from plib.stdlib.abstractcontainer import abstractcontainer

See the PLIB.CLASSES sub-package docstring and comments for more details.

This file itself currently includes:

variables pythonpath, plibpath, binpath, sharepath --
    contain pathnames to root python directory, plib directory,
    third-party binary directory, and third-party shared data directory
    (the latter two are where plib's scripts and example programs will
    have been installed)

function closure -- a reference to ``plib.stdlib.func.partial``,
    provided for convenience since the name is more indicative of
    the usage to some

function fix_newlines -- returns a string with line breaks changed
    from old_newline to newline.

function inrange -- returns index forced to be >= low, <= high.

function normalize -- returns index with negative values normalized
    relative to count.

function normalize_slice -- returns a list of indexes "covered" by a
    slice (normalized relative to count), or an integer giving the
    index to which a zero-length slice refers (normalized relative
    to count).

function slice_len -- returns the "length" of a slice (meaning the
    number of indexes that would be affected if it were used as an
    index into a sequence).

function split_string -- splits a string into three pieces, at the
    line breaks after the given start string and before the given
    end string appear. Note edge case behavior: if the start string
    is not found, the first of the three strings returned will be
    empty; if the end string is not found, the last of the three
    will be empty, and if both are not found, the middle of the
    three strings will be the entire string passed in. This may
    seem a little strange, but if you think about how you would use
    this function, it makes sense. (Note also that finding the
    start string really means that plus finding a newline after it,
    and finding the end string really means that plus finding a
    newline before it. This can be tweaked by setting the
    ``find_newlines`` argument to ``False``.)

functions strtobool, strtodate -- self-explanatory.

function type_from_name -- returns a type object corresponding
to ``name``.

constant universal_newline -- string representing the "universal
    newline" character

function upgrade_builtins -- convenience function to ensure
    that function names from more recent Python versions are
    in the builtin namespace even in earlier versions. See
    the function docstring for details.
"""

import sys
import datetime

from plib.utils import ModuleProxy

from _paths import *

from plib.stdlib.func import partial as closure


# Newline handling functions

universal_newline = '\n'

def split_string(s, newline, start, end, find_newlines=True):
    i = s.find(start)
    if i < 0:
        j = s.find(end)
    else:
        j = s.find(end, i)
        if find_newlines:
            i = s.find(newline, i) + len(newline)
        else:
            i += len(start)
    if (j > -1) and find_newlines:
        if i > -1:
            j = s.rfind(newline, i, j)
        else:
            j = s.rfind(newline, 0, j)
    if i < 0 and (j < 0):
        return "", s, ""
    if i < 0:
        return "", s[:j], s[j:]
    if j < 0:
        return s[:i], s[i:], ""
    return s[:i], s[i:j], s[j:]


def fix_newlines(s, newline, old_newline=universal_newline):
    result = newline.join(s.splitlines())
    if s.endswith(old_newline):
        return result + newline
    return result


# Sequence/slice handling functions

def inrange(index, v1, v2):
    """Force index to be within the range v1 to v2, and return result.
    """
    if v1 < v2:
        low = v1
        high = v2
    else:
        low = v2
        high = v1
    return min(max(index, low), high)


def normalize(count, index):
    """Return index with negative values normalized to count.
    
    Index values out of range after conversion will raise IndexError.
    """
    
    if index < 0:
        result = index + count
    else:
        result = index
    if (result < 0) or (result > count - 1):
        raise IndexError, "sequence index out of range"
    return result


def normalize_slice(count, index):
    """Return slice index normalized to count.
    
    Return one of the following, depending on the type of slice index:
    
    - For a non-empty slice (e.g., [x:y] where x != y), return a list of
      indexes to be affected;
    
    - For an empty slice (e.g., [x:x]), return the slice location (x)
      as an int.
    
    - For extended slices, if start and stop are the same, return an
      empty list; otherwise treat as a non-empty slice.
    
    The index(es) returned will be normalized relative to count, and indexes
    out of range after normalization will be truncated to range(0, count + 1).
    The extra index at count is to allow for the possibility of an append
    (a zero-length slice with index == count). Note that this means that,
    unlike the normalize function above, this function will never throw an
    exception due to values being out of range; this is consistent with the
    observed semantics of Python slice syntax, where even values way out of
    range are accepted and truncated to zero or the end of the sequence.
    The only exception this routine will throw is ValueError for a zero
    slice step.
    
    Note that if ``count`` is ``None``, any slice parameters that would require
    normalization (such as a negative ``start`` or ``stop``, a ``stop`` of
    ``None``, or a ``start`` of ``None`` with a negative ``step``) will raise
    ``IndexError``; this allows this function to be used transparently by
    sequences that have no known length, while still checking and processing
    slice indexes that are valid.
    """
    
    if index.step is None:
        step = 1
    else:
        step = int(index.step)
    if step == 0:
        raise ValueError, "Slice step cannot be zero."
    if index.start is None:
        if step < 0:
            if count is None:
                raise IndexError, "sequence index out of range"
            start = count - 1
        else:
            start = 0
    else:
        start = int(index.start)
        if start < 0:
            if count is None:
                raise IndexError, "sequence index out of range"
            start += count
    if index.stop is None:
        if step < 0:
            stop = -1
        else:
            if count is None:
                raise IndexError, "sequence index out of range"
            stop = count
    else:
        stop = int(index.stop)
        if stop < 0:
            if count is None:
                raise IndexError, "sequence index out of range"
            stop += count
    if start == stop:
        if step != 1:
            return []
        if count is None:
            return start
        return inrange(start, 0, count)
    elif (count is not None) and (
            (count == 0) or
            ((step > 0) and ((start >= count) or (start > stop))) or
            ((step < 0) and ((start < 0) or (start < stop))) ):
        return []
    else:
        if count is not None:
            start = inrange(start, 0, count - 1)
            if step < 0:
                stop = inrange(stop, -1, count - 1)
            else:
                stop = inrange(stop, 0, count)
        return range(start, stop, step)


def slice_len(s):
    """Return the number of indexes referenced by a slice.
    
    Note that we do not normalize the slice indexes, since we don't
    have a sequence length to reference them to. Also note that,
    because of this, we have to return None if there is no stop value,
    or if start or stop are negative.
    """
    
    if s.start is None:
        start = 0
    else:
        start = int(s.start)
    if start < 0:
        return None
    if s.stop is None:
        return None
    stop = int(s.stop)
    if stop < 0:
        return None
    if s.step is None:
        step = 1
    else:
        step = int(s.step)
    if step == 0:
        raise ValueError, "Slice step cannot be zero."
    if start == stop:
        return 0
    else:
        return (stop - start) // step


# Type conversion functions

def strtobool(s, falsestr='False', truestr='True'):
    """Return bool from string s interpreting s as a 'Python value string'.
    
    Return None if s is not 'True' or 'False'.
    """
    return {falsestr: False, truestr: True}.get(s, None)


def strtodate(s):
    """Return date object from string formatted as date.__str__ would return.
    """
    return datetime.date(*map(int, s.split('-')))


def type_from_name(name):
    """Return type object corresponding to ``name``.
    
    Currently searches only the built-in types. No checking is done to
    make sure the returned object is actually a type.
    """
    import __builtin__
    try:
        return getattr(__builtin__, name)
    except AttributeError:
        raise ValueError, "no type corresponding to %s" % name


### Convenience function to upgrade builtin namespace ###

BUILTIN_NAMES = [
    'all',
    'any',
    'bin',
    'next',
    'reversed',
    'sorted'
]

EXTRA_NAMES = [
    'first',
    'inverted',
    'last',
    'prod'
]

# This ensures we don't run the upgrade multiple times
_upgraded = False


def upgrade_builtins():
    """Upgrades __builtin__ namespace in earlier Python versions.
    
    This function is provided as a convenience for easier coding when using
    functions that are builtins in later Python versions, but which would
    normally have to be imported from plib.stdlib in earlier versions. For
    example, without this function, you would have to say::
    
        try:
            any
        except NameError:
            from plib.stdlib import any
    
    in order to ensure that the ``any`` function was accessible in your
    module. If you were using multiple such functions, this stanza would
    quickly become large and messy.
    
    An alternative to this function would be to put a similar stanza in the
    plib.stdlib code, so that such functions would always appear in the
    plib.stdlib namespace, whether they were builtins in the running Python
    version or not. However, this would still require you to say::
    
        from plib.stdlib import <builtin1>, <builtin2>, ...
    
    in your module, meaning that you would have to keep track of which
    builtins you were using module by module (or else use from import *,
    which is considered highly undesirable by all right-thinking Python
    programmers). Since the whole point of having built-in functions is to
    not have to do such things, this seems less than optimal.
    
    This function solves the problem as best it can be solved without major
    magical hackery at the time of importing plib.stdlib--which I may decide
    to try in future, so you have been warned. :-) But at present, this is
    the intended usage::
    
        # Do this somewhere in your code, usually at the end of imports
        from plib.stdlib import upgrade_builtins
        upgrade_builtins(__name__)
    
    This will add equivalent functions to the built-in namespace for all
    builtins from the following list that are not already present in the
    running version of Python. In addition, it will add the plib-specific
    "builtins" listed below, which are not provided by default in any
    current Python version, but which are so general and useful that IMHO
    they ought to be. :-) You only need to do this once, anywhere in your
    code, and the upgraded builtins will be available for the life of that
    invocation of the interpreter.
    
    Builtins currently provided:
    
    - all
    - any
    - bin
    - next
    - reversed
    - sorted
    
    Additional plib-specific "builtins":
    
    - first
    - inverted
    - last
    - prod
    """
    
    global _upgraded
    if not _upgraded:
        import __builtin__
        for builtin_name in BUILTIN_NAMES:
            if not hasattr(__builtin__, builtin_name):
                import _builtins
                setattr(__builtin__, builtin_name,
                    getattr(_builtins, builtin_name))
        for extra_name in EXTRA_NAMES:
            import _extras
            setattr(__builtin__, extra_name, getattr(_extras, extra_name))
        _upgraded = True

# *************** end of 'internal' functions for this module ***************

# Now we do the ModuleProxy magic to make classes in
# our sub-modules appear in our namespace

excludes = ['_builtins', '_extras',
    '_defaultdict', '_namedtuple', '_typed_namedtuple', '_iters',
    'cmdline', 'coll', 'decotools', 'func', 'imp', 'iters',
    'mail', 'mathlib', 'options', 'timer']

ModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals(),
    excludes=excludes)

# Now clean up our namespace
del ModuleProxy
