#!/usr/bin/env python
"""
Module _DEFAULTDICT -- Alternate implementation of defaultdict
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""


class defaultdict(dict):
    """A dict which sets keys to a default value when not present.
    
    The ``default_factory`` argument must be provided; if not,
    ``defaultdict`` acts just like a regular dict::
    
        >>> d = defaultdict()
        >>> d[0]
        Traceback (most recent call last):
         ...
        KeyError: 0
    
    Note that the inherited behavior includes propagating normal
    dict exceptions, such as for invalid key types::
    
        >>> d[list()]
        Traceback (most recent call last):
         ...
        TypeError: list objects are unhashable
    
    (NOTE: If the above doctest is run under Python 2.6, it will
    fail, because the exception message changed. This is not
    actually an issue since a TypeError is still thrown, but it's
    a nuisance, though not enough of one for me to hack a fix here.
    The failure does not arise in the PLIB test suite because the
    collections module has the defaultdict class in Python 2.6, so
    this doctest is never run; but it is noted here in case this
    module is tested directly instead of from the PLIB test suite.)
    
    The factory function takes no arguments and returns the
    value to be used as a default::
    
        >>> d = defaultdict(lambda: '0')
        >>> d
        {}
        >>> d[0]
        '0'
        >>> d
        {0: '0'}
    
    The default factory only comes into play if a key is not
    already in the dict::
    
        >>> d = defaultdict(lambda: '0', {1: '1'})
        >>> len(d)
        1
        >>> d[1]
        '1'
        >>> len(d)
        1
        >>> d[0]
        '0'
        >>> len(d)
        2
        >>> 
    """
    
    def __init__(self, default_factory=None, *args, **kwargs):
        self.default_factory = default_factory
        dict.__init__(self, *args, **kwargs)
    
    def __missing__(self, key):
        if self.default_factory is not None:
            value = self.default_factory()
            self[key] = value
            return value
        raise KeyError(key)
    
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
