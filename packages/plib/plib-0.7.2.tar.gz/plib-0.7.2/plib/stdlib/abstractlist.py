#!/usr/bin/env python
"""
Module abstractlist
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractlist class.
"""

import sys

from plib.stdlib import abstractsequence


class abstractlist(abstractsequence):
    """Fully mutable abstract sequence.
    
    Abstract base class to match list functionality but minimize the
    number of methods that must be implemented in subclasses.
    
    The only methods which *must* be implemented are __len__, __getitem__,
    __setitem__, and __delitem__. Also, it will almost always be necessary
    to override __init__ to initialize the underlying data structure *before*
    calling up to this class's __init__ (which will populate the data structure
    if a sequence is passed to the constructor). It may also be advantageous
    to reimplement __iter__ if a more efficient method of iterating through
    the underlying data structure exists (this will depend on how expensive
    the __getitem__ call is vs. the reimplemented iterator), and __contains__
    if a more efficient membership test exists. Finally, note that sort is
    not implemented in this class, since duplicating the built-in list.sort
    is highly problematic without knowledge of the underlying data structure;
    therefore sort functionality must be implemented as well if desired.
    
    The key, of course, is that, unlike the situation when one wants to
    subclass the built-in list class to overlay a different data structure,
    here you do *not* have to override all the other mutable sequence
    methods, append, insert, etc., because in this abstract class they all
    use the above methods to do their work. Another way of putting this
    point would be to raise the question whether the built-in Python
    list implementation, which does not have this feature, is a case of
    premature optimization. :)
    """
    
    def __init__(self, sequence=None):
        """Initialize the data structure from sequence.
        
        Subclasses should set up the underlying data structure *before*
        calling up to this method.
        """
        
        if sequence is not None:
            self.extend(sequence)
    
    # __len__, __getitem__, and __setitem__ are inherited from abstractsequence
    
    def __delitem__(self, index):
        """Delete item by index.
        
        Negative indexes are relative to end of sequence.
        Raise IndexError if index is out of range.
        """
        raise NotImplementedError
    
    if sys.version_info < (2, 0):
        # Include these only in old versions that require them
        def __getslice__(self, i, j):
            return self.__getitem__(slice(max(0, i), max(0, j)))
        def __setslice__(self, i, j, seq):
            self.__setitem__(slice(max(0, i), max(0, j)), seq)
        def __delslice__(self, i, j):
            self.__delitem__(slice(max(0, i), max(0, j)))
    
    # __iter__, __contains__, and the comparison and arithmetic operators are
    # inherited from abstractsequence
    
    # index, count, and reverse are inherited from abstractsequence
    
    def append(self, value):
        self.extend((value,))
    
    def extend(self, sequence):
        self[len(self):len(self)] = sequence
    
    def insert(self, index, value):
        self[index:index] = (value,)
    
    def remove(self, value):
        del self[self.index(value)]
    
    def pop(self, index=-1):
        result = self[index]
        del self[index]
        return result
    
    def sort(self, cmp=None, key=str.lower, reverse=False):
        """Sort the sequence items in place.
        """
        raise NotImplementedError
    
    # We add this one method here for convenience although normally only
    # mappings have it, not sequences
    
    def clear(self):
        while len(self):
            self.pop()


try:
    from collections import MutableSequence
except ImportError:
    pass
else:
    MutableSequence.register(abstractlist)
