#!/usr/bin/env python
"""
Module AbstractMappingMixin
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AbstractMappingMixin class.
"""

from plib.stdlib import AbstractKeyedMixin


class AbstractMappingMixin(AbstractKeyedMixin):
    """Mixin class for mapping with fixed keys but mutable values.
    
    Supports key checking on item assignment, enforcing the
    rule that the mapping's set of keys cannot change.
    """
    
    def _set_value(self, key, value):
        """Set value corresponding to key.
        
        This method will only be called for keys that are known to
        be in the mapping.
        """
        raise NotImplementedError
    
    def __setitem__(self, key, value):
        if key in self._keylist():
            self._set_value(key, value)
        else:
            raise KeyError(repr(key))
