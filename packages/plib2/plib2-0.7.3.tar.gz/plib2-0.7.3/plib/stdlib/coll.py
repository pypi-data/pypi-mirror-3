#!/usr/bin/env python
"""
Module COLL -- Convenience Collection Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains some additional collection classes
with method names redefined for greater convenience. The
key desire here is to have the method names 'append' and
'next' refer to the methods that you *want* to call for
each collection to add and retrieve an item from the
"right" place (i.e., the "next" item for the given
collection). Thus:

fifo -- a deque; 'append' adds to the end of the queue,
    'next' retrieves from the start (i.e., 'popleft').

stack -- a list; 'append' adds to the end of the list,
    'next' retrieves from the end as well (i.e., 'pop').

Note that the contents of the standard library collections
module are also available here, so you can just import
from here instead of having to import both modules. This
includes equivalents of classes that appear in later
Python versions (defaultdict and/or namedtuple) for earlier
Python versions that don't include them.
"""

import sys
from collections import *

try:
    defaultdict
except NameError:
    from plib.stdlib._defaultdict import defaultdict

try:
    namedtuple
except NameError:
    from plib.stdlib._namedtuple import namedtuple

from plib.stdlib._typed_namedtuple import typed_namedtuple


class fifo(deque):
    """A first-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.next = self.popleft
        deque.__init__(self, *args, **kwargs)


class stack(list):
    """A last-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.next = self.pop
        list.__init__(self, *args, **kwargs)


def merge_dict(target, source):
    """Merges source into target
    
    Only updates keys not already in target.
    """
    
    merges = dict((key, value) for key, value in source.iteritems()
        if key not in target)
    target.update(merges)
