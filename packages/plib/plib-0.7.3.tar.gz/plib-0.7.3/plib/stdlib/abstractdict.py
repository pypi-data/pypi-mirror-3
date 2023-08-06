#!/usr/bin/env python
"""
Module abstractdict
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractdict class.
"""

from plib.stdlib import abstractmapping


class abstractdict(abstractmapping):
    """Fully mutable abstract dictionary.
    
    Abstract base class to match dict functionality but minimize the
    number of methods that must be implemented in subclasses.
    
    The only methods which *must* be implemented are __iter__, __getitem__,
    __setitem__, and __delitem__. Also, it will almost always be necessary
    to override __init__ to initialize the underlying data structure *before*
    calling up to this class's __init__ (which will populate the data structure
    if a mapping or keyword arguments are passed to the constructor). It may
    also be advantageous to reimplement __contains__ and/or __len__ if more
    efficient algorithms specific to the underlying data structure can be
    used.
    
    The key, of course, is that, unlike the situation when one wants to
    subclass the built-in dict class to overlay a different data structure,
    here you do *not* have to override all the other mutable mapping
    methods, update, clear, etc., because in this abstract class they all
    use the above methods to do their work. Another way of putting this
    point would be to raise the question whether the built-in Python
    dict implementation, which does not have this feature, is a case of
    premature optimization. :)
    """
    
    def __init__(self, mapping=None, **kwargs):
        """Initialize the data structure from mapping.
        
        Subclasses should set up the underlying data structure *before*
        calling up to this method.
        """
        
        if mapping or kwargs:
            self.update(mapping, **kwargs)
    
    # Note: __setitem__ should add key and its corresponding value
    # to the mapping if key is not in the current list of keys.
    # This behavior is changed from abstractmapping.
    
    def __delitem__(self, key):
        """Remove key and its corresponding value from the mapping.
        """
        raise NotImplementedError
    
    def clear(self):
        # Realize the key list to avoid issues when mutating the mapping
        for k in list(self.iterkeys()):
            del self[k]
    
    def copy(self):
        return self.__class__(self)
    
    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default
    
    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got " +
                repr(1 + len(args)))
        try:
            value = self[key]
        except KeyError:
            if args:
                return args[0]
            raise
        del self[key]
        return value
    
    def popitem(self):
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError("container is empty")
        del self[k]
        return (k, v)
    
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
    fromkeys = classmethod(fromkeys)


try:
    from collections import MutableMapping
except ImportError:
    pass
else:
    MutableMapping.register(abstractdict)
