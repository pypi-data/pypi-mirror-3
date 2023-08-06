#!/usr/bin/env python
"""
Module abstractkeyed
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractkeyed class.
"""

from __future__ import generators # to ensure we can use yield in version 2.2

import sys

from plib.stdlib import upgrade_builtins
upgrade_builtins()


class abstractkeyed(object):
    """Immutable abstract key-value mapping.
    
    The intent of this class, like its counterpart for sequences,
    ``abstractcontainer``, is to minimize the amount of work needed
    to make a data structure support the Python mapping interface.
    Derived classes only need to implement the ``__iter__`` and
    ``__getitem__`` methods (they may also override the ``__len__``
    and ``__contains__`` methods if faster implementations are
    available). This mapping is immutable; increasing levels of
    mutability are provided by ``abstractmapping`` and
    ``abstractdict``.
    """
    
    def __iter__(self):
        """Iterate over the allowed keys for this mapping.
        """
        raise NotImplementedError
    
    def __getitem__(self, key):
        """Return the value corresponding to key.
        
        Raise ``KeyError`` if ``key`` is not in the list of allowed keys.
        """
        raise NotImplementedError
    
    # Strictly speaking, these should not be needed, since Python should
    # automatically raise TypeError if item assignment or deletion is
    # attempted using subscript notation (a[k] = x, del a[k]) on an object
    # that doesn't have a __setitem__ or __delitem__ defined. However, there
    # appear to be some quirks in the implementation where AttributeError
    # gets raised instead, so we implement the methods here for consistent
    # semantics. See the abstractcontainer source for more info.
    
    def __setitem__(self, key, value):
        raise TypeError, "object does not support item assignment"
    
    def __delitem__(self, key):
        raise TypeError, "object does not support item deletion"
    
    #def __repr__(self):
    #    return "".join(("{", ", ".join(["%s: %s" % (repr(k), repr(v))
    #        for k, v in self.iteritems()]), "}"))
    #
    #__str__ = __repr__
    
    # Default implementation of size and membership test; note that we
    # have to be careful which version we're under for using generators and
    # generator expressions (see the abstractcontainer source for more info)
    
    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True
    
    if sys.version_info < (2, 4):
        
        # Can't use generator expression so we need a helper
        
        def __len_helper(self):
            for k in self:
                yield 1
        
        def __len__(self):
            return sum(self.__len_helper())
    
    else:
        
        def __len__(self):
            return sum(1 for k in self)
    
    # Basic comparison, should work just like comparing a regular dict
    # (this will not be speedy, but iterating through the keys and values
    # of both objects wouldn't be either, and this way we don't have to
    # reimplement all the dict comparison code; derived classes that can
    # produce a better implementation should override)
    
    def __cmp__(self, other):
        return cmp(dict(self), other)
    
    # Implement other methods that don't mutate the object or require
    # initializing another object of the same class (e.g., copy). Note
    # that we don't attempt to implement "dict views" for the keys,
    # values, and items methods, nor do we attempt to construct objects
    # for them with set semantics; in fact, I'd prefer not to have them
    # at all, but Python refuses to treat instances of this class as
    # mappings without them (keys in particular)
    
    def iterkeys(self):
        for k in self:
            yield k
    
    def itervalues(self):
        for k in self:
            yield self[k]
    
    def iteritems(self):
        for k in self:
            yield k, self[k]
    
    def keys(self):
        return list(self.iterkeys())
    
    def values(self):
        return list(self.itervalues())
    
    def items(self):
        return list(self.iteritems())
    
    def has_key(self, key):
        return key in self
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


try:
    from collections import Mapping
except ImportError:
    pass
else:
    Mapping.register(abstractkeyed)
