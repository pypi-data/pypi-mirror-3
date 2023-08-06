#!/usr/bin/env python
"""
Module AttrDict
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AttrDict class.
"""

from plib.stdlib import AttrDelegate, basekeyed


class AttrDict(AttrDelegate, basekeyed):
    """Make an object with attributes support a mapping interface.
    
    Only attributes defined in the attribute list passed to this
    class will appear as allowed keys in the mapping. The
    mapping is immutable (since it is only supposed to be
    "assigned" to during initialization).
    """
    
    def __init__(self, keylist, obj):
        AttrDelegate.__init__(self, obj)
        self._keys = keylist
    
    def _keylist(self):
        return self._keys
    
    def _get_value(self, key):
        return getattr(self, key)
