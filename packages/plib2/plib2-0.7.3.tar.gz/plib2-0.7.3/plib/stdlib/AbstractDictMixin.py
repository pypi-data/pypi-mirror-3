#!/usr/bin/env python
"""
Module AbstractDictMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AbstractDictMixin class.
"""

from plib.stdlib import AbstractMappingMixin


class AbstractDictMixin(AbstractMappingMixin):
    """Mixin class for fully mutable abstract mapping.
    
    Provides default implementations of all mutable mapping methods
    based on the core key/value get/set/add/delete methods.
    """
    
    def _add_key(self, key, value):
        """Add key and value to the mapping.
        
        Will only be called if key is not currently in the mapping.
        """
        raise NotImplementedError
    
    def _del_key(self, key):
        """Remove key and its corresponding value from the mapping.
        
        Will only be called if key is currently in the mapping.
        """
        raise NotImplementedError
    
    def __setitem__(self, key, value):
        if key in self._keylist():
            self._set_value(key, value)
        else:
            self._add_key(key, value)
    
    def __delitem__(self, key):
        if key in self._keylist():
            self._del_key(key)
        else:
            raise KeyError(repr(key))
