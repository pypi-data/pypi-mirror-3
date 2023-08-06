#!/usr/bin/env python
"""
Module basesequence
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the basesequence class.
"""

from plib.stdlib import AbstractSequenceMixin, abstractsequence


class basesequence(AbstractSequenceMixin, abstractsequence):
    """Base class for fixed-length abstract sequence.
    
    An abstract sequence whose length cannot be changed. Implements
    argument checking on item assignment to enforce this restriction.
    
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
    pass
