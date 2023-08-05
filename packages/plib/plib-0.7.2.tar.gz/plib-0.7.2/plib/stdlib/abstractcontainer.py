#!/usr/bin/env python
"""
Module abstractcontainer
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractcontainer class.
"""

from __future__ import generators # to ensure we can use yield in version 2.2

import sys
from itertools import izip

from plib.stdlib import inrange, upgrade_builtins
upgrade_builtins()


class abstractcontainer(object):
    """Immutable abstract container.
    
    An abstract class to provide the minimal possible support of the
    Python container protocol. Subclasses can implement just the __len__
    and __getitem__ methods to allow the class to be used in the standard
    Python container idioms like for item in container, etc. This
    container is immutable, so its length and its items cannot be
    changed (increasing levels of mutability are provided by the
    abstractsequence and abstractlist classes); note that this does
    *not* mean the underlying data structure must be immutable, only
    that the view of it provided by this container class is.
    """
    
    def __len__(self):
        """Return the number of items in the container.
        """
        raise NotImplementedError
    
    def __getitem__(self, index):
        """Get item by index.
        
        Negative indexes are relative to end of list.
        Raise IndexError if index is out of range.
        """
        raise NotImplementedError
    
    # Strictly speaking, these should not be needed, since Python should
    # automatically raise TypeError if item assignment or deletion is
    # attempted using subscript notation (a[i] = x, del a[i]) on an object
    # that doesn't have a __setitem__ or __delitem__ defined. However, there
    # appear to be some quirks in the implementation where AttributeError
    # gets raised instead (probably not all code paths in the interpreter
    # that look for the methods were caught, but I haven't had time to try
    # to grok the source code...), so these methods are here to guarantee
    # consistent behavior. Note, however, that this means that explicit calls
    # to __setitem__ and __delitem__ will also raise TypeError, instead of
    # AttributeError, which is what gets raised on built-in unsubscriptable
    # objects like None. This shouldn't be a big deal.
    
    def __setitem__(self, index, value):
        raise TypeError, "object does not support item assignment"
    
    def __delitem__(self, index):
        raise TypeError, "object does not support item deletion"
    
    #def __repr__(self):
    #    return "".join(("[", ", ".join([repr(item) for item in self]), "]"))
    #
    #__str__ = __repr__
    
    # Default implementation of iteration and membership test; note that we
    # have to be careful which version we're under for using generators and
    # generator expressions, to avoid having to realize intermediate sequences
    # (i.e., we could use any with a list comp, but that would realize the
    # intermediate list)
    
    def __iter__(self):
        for index in xrange(len(self)):
            yield self[index]
    
    if sys.version_info < (2, 4):
        
        # Can't use generator expression so we need a helper
        
        def __contains_helper(self, value):
            for item in self:
                yield item == value
        
        def __contains__(self, value):
            return any(self.__contains_helper(value))
    
    else:
        
        def __contains__(self, value):
            return any(item == value for item in self)
    
    # We can always provide this since our upgrade_builtins (above) adds
    # a ``reversed`` builtin function that will use it
    
    def __reversed__(self):
        for i in reversed(xrange(len(self))):
            yield self[i]
    
    # Need the basic comparison operators
    
    if sys.version_info < (2, 4):
        
        def __ne_helper(self, other):
            for x, y in izip(self, other):
                yield x != y
        
        def __ne__(self, other):
            return (len(other) != len(self)) or \
                any(self.__ne_helper(other))
    
    else:
        
        def __ne__(self, other):
            return (len(other) != len(self)) or \
                any(x != y for x, y in izip(self, other))
    
    def __eq__(self, other):
        return not self.__ne__(other)
    
    def __lt__(self, other):
        return (len(self) < len(other))
    
    def __gt__(self, other):
        return (len(self) > len(other))
    
    def __le__(self, other):
        return (len(self) <= len(other))
    
    def __ge__(self, other):
        return (len(self) >= len(other))
    
    # We put these in to ensure we don't get caught by subtle differences
    # in how operator compatibility is computed in different Python versions;
    # we want to disallow all arithmetic unless a derived class explicitly
    # includes the capability.
    
    def __add__(self, other):
        raise TypeError, "operation not supported"
    
    def __radd__(self, other):
        raise TypeError, "operation not supported"
    
    def __iadd__(self, other):
        raise TypeError, "operation not supported"
    
    def __mul__(self, other):
        raise TypeError, "operation not supported"
    
    def __rmul__(self, other):
        raise TypeError, "operation not supported"
    
    def __imul__(self, other):
        raise TypeError, "operation not supported"
    
    # These are implemented here because they don't mutate the object
    
    def index(self, value, start=None, end=None):
        if start is None:
            start = 0
        if end is None:
            end = len(self)
        if start < 0:
            start += len(self)
        start = inrange(start, 0, len(self))
        if end < 0:
            end += len(self)
        end = inrange(end, 0, len(self))
        for i in xrange(start, end):
            if self[i] == value:
                return i
        raise ValueError, "sequence item not found"
    
    if sys.version_info < (2, 4):
        
        # Can't use a generator expression so we need a helper
        def __count_helper(self, value):
            for item in self:
                yield int(item == value)
        
        def count(self, value):
            return sum(self.__count_helper(value))
    
    else:
        
        def count(self, value):
            return sum(int(item == value) for item in self)


try:
    from collections import Sequence
except ImportError:
    pass
else:
    Sequence.register(abstractcontainer)
