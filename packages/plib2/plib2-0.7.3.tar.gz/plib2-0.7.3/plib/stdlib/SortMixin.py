#!/usr/bin/env python
"""
Module SortMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the SortMixin class.
"""


class SortMixin(object):
    """
    Mixin class to allow insertion of objects into sequences
    in proper sorted order. Will work with any class that
    implements the insert method (note that calling insert
    with an index of len(self) should append the value to
    the end of the sequence, in accordance with the Python
    list semantics). For best results, if this mixin is used
    with a sequence class, the insert_sorted method should be
    the *only* method used to add new items to the sequence;
    otherwise it is not guaranteed that the binary-tree insert
    algorithm will work properly (since it depends on the
    sequence being sorted correctly before insertion).
    
    The sort function used to compare values can be changed
    by passing a sort function to the insert_sorted method.
    This will only affect that particular insertion (meaning
    that, to use your custom sort function for all insertions,
    you have to pass it by hand to insert_sorted every time).
    There is currently no provision for defining a class-wide
    sort function to override the cmp builtin (which would
    affect all insertions), because there is no easy way to
    ensure that it will take the correct number of arguments;
    for example, the following code, which is the "obvious"
    way to implement a custom sort function, does *not* work:
        
        def testcmp(x, y):
            return cmp(str(x), str(y))
        class SortMixin2(SortMixin):
            default_sortfunc = testcmp
            def insert_sorted(self, value, sortfunc=None):
                if sortfunc is None:
                    sortfunc = self.default_sortfunc
                super(SortMixin2, self).insert_sorted(value, sortfunc)
    
    This code will raise a TypeError because the sort function,
    testcmp, takes only two arguments, but it is passed three;
    this is because retrieving it as an instance attribute
    (self.default_sortfunc) makes it into a bound method, which
    prepends self to the argument list. (Note that this does
    *not* happen with built-in functions like cmp.) So the only
    way to make something like this work would be to make your
    custom sort function a method on the class, and if you do
    that, you can explicitly override insert_sorted to use it
    anyway, so there's no point in adding such code to SortMixin.
    """
    
    #default_sortfunc = cmp
    
    def _btree_index(self, value, sortfunc):
        # Return proper index to insert value based on sortfunc.
        start = 0
        end = len(self) - 1
        while start <= end:
            i = start + ((end - start) // 2)
            s = sortfunc(value, self[i])
            if s < 0:
                if i == 0:
                    # It's before all items in the list
                    return i
                end = i - 1
            elif s > 0:
                if i == (len(self) - 1):
                    # It's after all items in the list
                    return len(self)
                start = i + 1
            else:
                # Insert *after* equal value that's already in the list
                return i + 1
        # It's between end and start, end < start so start is
        # where it goes
        return start
    
    def insert_sorted(self, value, sortfunc=None, key=None):
        """Insert value in its proper place based on sorting function.
        """
        
        if sortfunc is None:
            if key is not None:
                sortfunc = lambda x, y: cmp(key(x), key(y))
            else:
                sortfunc = cmp #self.default_sortfunc
        self.insert(self._btree_index(value, sortfunc), value)
