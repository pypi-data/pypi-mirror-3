#!/usr/bin/env python
"""
Module AbstractContainerMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AbstractContainerMixin class.
"""

from __future__ import generators # to ensure we can use yield in version 2.2

import sys

from plib.stdlib import normalize, normalize_slice


class AbstractContainerMixin(object):
    """Mixin class for immutable abstract container.
    
    Support slice operations and normalization of indexes. This class is
    immutable; increasing levels of mutability are provided by
    ``AbstractSequenceMixin`` and ``AbstractListMixin``.
    
    Note that, because this class is immutable and we can't provide a
    constructor without knowing the underlying data storage implementation,
    the slice_class field is provided to allow derived classes to specify
    which class to use when returning slices (e.g., x = s[i:j]). This means
    that these abstract containers are not guaranteed to return slices that
    are of the same type as themselves, although the slice_class should be
    chosen to make them completely compatible functionally.
    """
    
    slice_class = tuple
    
    def _get_data(self, index):
        """Return a single item by index.
        
        (Slice arguments to ``__getitem__`` may result in multiple calls
        to this method).
        """
        raise NotImplementedError
    
    def _index_ok(self, index):
        """Validate, and if necessary normalize, index.
        
        If ``index`` is an int, it must be within the valid sequence
        range (0 to len - 1), after correcting negative indexes relative
        to the end of the sequence. If so, return it; otherwise raise
        ``IndexError``. (The ``normalize`` function is used to accomplish
        this.)
        
        If index is a slice, normalize it (by calling ``normalize_slice``)
        and return a 2-tuple of (slice length, normalize_slice result).
        No exceptions are thrown here for slices; that is left up to
        the caller (since here we don't know whether zero-length slices
        are allowed or not).
        
        Sequences that do not have a known length (e.g., instances of
        the ``IndexedGenerator`` decorator class) will raise ``IndexError``
        if any negative indexes are given, either as single indexes or
        slice elements.
        """
        
        try:
            normlen = len(self)
        except TypeError:
            normlen = None
        if isinstance(index, (int, long)):
            if normlen is None:
                if index < 0:
                    raise IndexError, "sequence index out of range"
                return index
            return normalize(normlen, index)
        elif isinstance(index, slice):
            n = normalize_slice(normlen, index)
            if isinstance(n, (int, long)):
                return (0, n)
            return (len(n), n)
        else:
            raise TypeError, "sequence index must be an integer or a slice"
    
    if sys.version_info < (2, 4):
        
        # Can't use generator expressions before 2.4, so we need a
        # helper function to avoid realizing the intermediate list
        def __getitem_helper(self, indexes):
            for i in indexes:
                yield self._get_data(i)
        
        def __getitem__(self, index):
            index = self._index_ok(index)
            if isinstance(index, tuple):
                length, indexes = index
                if length > 0:
                    return self.slice_class(self.__getitem_helper(indexes))
                return self.slice_class()
            return self._get_data(index)
    
    else:
        
        def __getitem__(self, index):
            index = self._index_ok(index)
            if isinstance(index, tuple):
                length, indexes = index
                if length > 0:
                    return self.slice_class(self._get_data(i) for i in indexes)
                return self.slice_class()
            return self._get_data(index)
