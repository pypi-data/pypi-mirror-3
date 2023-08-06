#!/usr/bin/env python
"""
Module _BUILTINS -- Alternate implementations for older Python versions
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from __future__ import generators # to ensure we can use yield in version 2.2

import sys
from itertools import chain, ifilter, ifilterfalse


def all(iterable):
    """Return True only if all elements of iterable are True.
    """
    for element in ifilterfalse(bool, iterable):
        return False
    return True


def any(iterable):
    """Return True if any element of iterable is True.
    """
    for element in ifilter(bool, iterable):
        return True
    return False


_hexmap = {
    '0': '0000',
    '1': '0001',
    '2': '0010',
    '3': '0011',
    '4': '0100',
    '5': '0101',
    '6': '0110',
    '7': '0111',
    '8': '1000',
    '9': '1001',
    'a': '1010',
    'b': '1011',
    'c': '1100',
    'd': '1101',
    'e': '1110',
    'f': '1111' }

def bin(n, hexmap=_hexmap):
    """Return a string representation of n in binary.
    """
    return '0b' + ''.join(list(hexmap[hexdigit]
        for hexdigit in hex(n)[2:].lower())).lstrip('0')


def next(it, default=None):
    """Return the next element of iterator, or default.
    """
    try:
        return it.next()
    except StopIteration:
        return default


if sys.version_info < (2, 4):
    
    # The helper function allows us to avoid chaining iterators
    # when seq has a __reversed__ method
    
    def _reversed_helper(seq):
        for i in xrange(len(seq) - 1, -1, -1):
            yield seq[i]
    
    def reversed(seq):
        """Return iterator over seq in reversed order.
        """
        if hasattr(seq, '__reversed__'):
            return seq.__reversed__()
        return _reversed_helper(seq)


else:
    
    def reversed(seq):
        """Return iterator over seq in reversed order.
        """
        if hasattr(seq, '__reversed__'):
            return seq.__reversed__()
        return (seq[i] for i in xrange(len(seq) - 1, -1, -1))


def sorted(iterable, *args, **kwargs):
    """Return sorted list from items in iterable.
    """
    result = list(iterable)
    result.sort(*args, **kwargs)
    return result
