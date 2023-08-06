#!/usr/bin/env python
"""
Sub-Package UTILS of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains general utility functions. It also
contains the ModuleProxy class (which is imported to appear
in the plib.utils namespace), which is used by several other
PLIB sub-packages--see the PLIB.CLASSES sub-package docstring
for details.

Utility functions currently provided:

recurselist, recursedict -- when you have a class field that's
    a container, these functions provide a way of combining all
    the values in your class's MRO, so you don't have to repeat
    them in derived classes.

locate -- generator that yields all filenames starting at a
    root location (by default, the current directory) that match
    a given pattern.
"""

import os
import fnmatch

from ModuleProxy import ModuleProxy


def _recurse(klass, name, result, methodname):
    method = getattr(result, methodname)
    for c in klass.__mro__:
        if name in c.__dict__:
            method(c.__dict__[name])
    return result


def recurselist(klass, name):
    """
    Recurses through mro of klass, assuming that where
    the class attribute name is found, it is a list;
    returns a list concatenating all of them.
    """
    return _recurse(klass, name, [], 'extend')


def recursedict(klass, name):
    """
    Recurses through mro of klass, assuming that where
    the class attribute name is found, it is a dict;
    returns a dict combining all of them.
    """
    return _recurse(klass, name, {}, 'update')


def _gen_names(path, seq, pattern):
    for name in (os.path.abspath(os.path.join(path, item))
        for item in seq if fnmatch.fnmatch(item, pattern)):
            yield name


def locate(pattern, root=os.getcwd(), include_dirs=False):
    """
    Generates all filenames in the directory tree starting at
    root that match pattern. Does not include subdirectories by
    default; this can be overridden with the include_dirs
    parameter. If subdirectories are included, they are yielded
    before regular files in the same directory.
    """
    for path, dirs, files in os.walk(root):
        if include_dirs:
            for name in _gen_names(path, dirs, pattern):
                yield name
        for name in _gen_names(path, files, pattern):
            yield name
