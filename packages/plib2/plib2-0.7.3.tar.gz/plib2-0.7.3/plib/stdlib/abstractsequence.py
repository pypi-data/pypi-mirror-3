#!/usr/bin/env python
"""
Module abstractsequence
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractsequence class.
"""

from plib.stdlib import abstractcontainer


class abstractsequence(abstractcontainer):
    """Fixed-length abstract sequence.
    
    An abstract sequence whose length cannot be changed.
    
    This class can be used to provide a sequence-like view of data
    structures whose length should not be mutable, but whose elements
    can be re-bound to new objects (unlike a tuple, whose elements
    can't be changed, although if the element objects themselves are
    mutable, they can be mutated in-place).
    
    Note: this class does not implement any mechanism to initialize
    the sequence from another one (i.e., to be able to call the
    constructor with another sequence as an argument, as the tuple
    constructor can be called). Subclasses that desire such a
    mechanism must implement it with an overridden constructor, and
    must ensure that the mechanism is compatible with the __len__
    and __setitem__ methods (so that those methods will not return
    an index out of range error during the initialization process).
    """
    
    # __len__, __getitem__, __iter__, and __contains__
    # are inherited from abstractcontainer
    
    def __setitem__(self, index, value):
        """Set item by index.
        
        Negative indexes are relative to end of sequence.
        Raise IndexError if index is out of range.
        """
        raise NotImplementedError
    
    # comparison and arithmetic operators inherited from abstractcontainer
    
    # index and count inherited from abstractcontainer
    
    def reverse(self):
        n = len(self)
        for i in xrange(n//2):
            self[i], self[n-i-1] = self[n-i-1], self[i]
