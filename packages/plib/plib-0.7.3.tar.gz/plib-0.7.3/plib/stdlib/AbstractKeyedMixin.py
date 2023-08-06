#!/usr/bin/env python
"""
Module AbstractKeyedMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AbstractKeyedMixin class.
"""


class AbstractKeyedMixin(object):
    """Mixin class for immutable abstract key-value mapping.
    
    Implements the standard container methods by assuming that
    the object has a list of its valid keys, and knows how to
    retrieve a value for each key; this knowledge should be
    implemented in derived classes in the private ``_keylist``
    and ``_get_value`` methods. Once these two methods are provided,
    the entire immutable mapping interface will work. (Derived
    classes will most likely also need to implement a constructor
    to initially populate the underlying data structure that the
    ``_keylist`` and ``_get_value`` methods access.)
    """
    
    def _keylist(self):
        """Return container of valid keys for this mapping.
        """
        raise NotImplementedError
    
    def _get_value(self, key):
        """Return value corresponding to key.
        
        This method will only be called for keys that are known to
        be in the mapping.
        """
        raise NotImplementedError
    
    def __getitem__(self, key):
        if key in self._keylist():
            return self._get_value(key)
        raise KeyError(repr(key))
    
    def __iter__(self):
        return iter(self._keylist())
    
    # We expect this to be faster than the default implementation
    # because _keylist() should be O(1) for length checks
    
    def __len__(self):
        return len(self._keylist())
