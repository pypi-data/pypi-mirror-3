#!/usr/bin/env python
"""
Module AttrList
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AttrList class.
"""

from plib.stdlib import AttrDelegate, basecontainer


class AttrList(AttrDelegate, basecontainer):
    """Make an object with attributes support a sequence interface.
    
    Only indexes in a valid range for the list of attribute names
    passed in will be valid indexes into the sequence (each index
    will access the attribute with the corresponding name in the
    list of names passed in). The sequence is immutable.
    """
    
    def __init__(self, names, obj):
        AttrDelegate.__init__(self, obj)
        self._names = names
    
    def __len__(self):
        return len(self._names)
    
    def _get_data(self, index):
        return getattr(self, self._names[index])
