#!/usr/bin/env python
"""
Module AbstractListMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AbstractListMixin class.
"""

from plib.stdlib import AbstractSequenceMixin


class AbstractListMixin(AbstractSequenceMixin):
    """Mixin class for fully mutable abstract sequence.
    
    Provides default implementations of all mutable sequence methods
    based on the core data get/set/add/delete methods.
    """
    
    slice_class = list
    
    def _add_data(self, index, value):
        """Insert a single item at index.
        
        (Zero-length slice arguments to ``__setitem__`` will result in
        one call to this method for each item in the value being set).
        If index == self.__len__(), this method should append value to
        the sequence.
        """
        raise NotImplementedError
    
    def _del_data(self, index):
        """Delete a single item by index.
        
        (Slice arguments to ``__delitem__`` may result in multiple
        calls to this method).
        """
        raise NotImplementedError
    
    def _add_items(self, index, value):
        for j, v in enumerate(value):
            self._add_data(index + j, v)
    
    def _del_items(self, indexes):
        # Delete in inverse order to minimize movement of items higher in list
        for i in reversed(indexes):
            self._del_data(i)
    
    def _rep_items(self, indexes, value):
        self._del_items(indexes)
        self._add_items(indexes[0], value)
    
    def __delitem__(self, index):
        index = self._index_ok(index)
        if isinstance(index, tuple):
            length, index = index
            if length > 0:
                self._del_items(index)
        else:
            self._del_data(index)
