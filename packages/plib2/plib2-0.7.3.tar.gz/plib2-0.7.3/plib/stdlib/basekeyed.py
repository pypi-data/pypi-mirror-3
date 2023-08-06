#!/usr/bin/env python
"""
Module basekeyed
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the basekeyed class.
"""

from plib.stdlib import AbstractKeyedMixin, abstractkeyed


class basekeyed(AbstractKeyedMixin, abstractkeyed):
    """Base class for immutable key-value mapping.
    
    The intent of this class, like its counterpart for sequences,
    ``basecontainer``, is to minimize the amount of work needed
    to make a data structure support the Python mapping interface.
    Derived classes only need to implement the ``_keylist`` and
    ``_get_value`` methods. This mapping is immutable; increasing
    levels of mutability are provided by ``basemapping`` and
    ``basedict``.
    """
    pass
