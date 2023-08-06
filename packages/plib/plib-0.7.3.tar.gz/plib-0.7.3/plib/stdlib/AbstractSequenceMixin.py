#!/usr/bin/env python
"""
Module AbstractSequenceMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AbstractSequenceMixin class.
"""

from itertools import izip

from plib.stdlib import AbstractContainerMixin


class AbstractSequenceMixin(AbstractContainerMixin):
    """Mixin class for fixed-length abstract sequence.
    
    Supports argument checking on item assignment, enforcing the
    rule that the sequence's length cannot change.
    """
    
    def _set_data(self, index, value):
        """Store a single item by index.
        
        (Slice arguments to ``__setitem__`` may result in multiple calls
        to this method).
        """
        raise NotImplementedError
    
    def __setitem__(self, index, value):
        # NOTE: the treatment of extended slices matches Python 2.6
        # list semantics; that means that, unlike in 2.5 and earlier,
        # extended slices with step == 1 are treated exactly the same
        # as non-extended slices
        extended = isinstance(index, slice) and (index.step is not None) and \
            (index.step != 1)
        index = self._index_ok(index)
        if isinstance(index, tuple):
            if value is self:
                # protect against a[::-1] = a
                value = tuple(value)
            try:
                vlength = len(value)
            except TypeError:
                try:
                    # NOTE: no way to avoid realizing generators/iterators
                    # here; we use tuple because it's faster to construct
                    # than list. As far as I can tell, the Python interpreter
                    # does the same thing for comparing the lengths of values
                    # and slices; the difference is that the interpreter only
                    # does it for extended slices, but we have to do it here
                    # even for a standard slice. This means, of course, that
                    # for fully mutable sequences (like AbstractMixin) and
                    # standard slices, we make an extra copy of the value when
                    # we don't really have to. For the use cases I've had thus
                    # far, this is not a major issue, because I've almost
                    # never had to use slicing, and when I do it's always
                    # small slices; also, typically the overhead of the
                    # individual item inserts (e.g., if each item is a row
                    # in a GUI table or a node in a GUI tree view) is much
                    # higher than the overhead of copying the object pointer
                    # into a tuple. Your mileage may vary.
                    value = tuple(value)
                    vlength = len(value)
                except TypeError:
                    raise TypeError("can only assign an iterable")
            length, index = index
            if (length < 1) and not extended:
                if vlength != 0:
                    self._add_items(index, value)
            elif length != vlength:
                if extended:
                    raise ValueError(
                        "attempt to assign sequence of length %i "
                        "to extended slice of length %i" %
                        (vlength, length))
                self._rep_items(index, value)
            else:
                for i, v in izip(index, value):
                    self._set_data(i, v)
        else:
            self._set_data(index, value)
    
    # These methods allow easy factoring out of the differences
    # between fixed-length and fully mutable sequences
    
    def _add_items(self, index, value):
        raise TypeError, "object does not support item insert/append"
    
    def _rep_items(self, indexes, value):
        raise ValueError, "object length cannot be changed"
    
    # Alternate implementation of reverse using extended slicing (should
    # be faster than the explicit for loop in abstractsequence.reverse)
    
    def reverse(self):
        l = len(self)
        c = l // 2
        d = l - c
        self[0:c:1], self[l-1:d-1:-1] = self[l-1:d-1:-1], self[0:c:1]
