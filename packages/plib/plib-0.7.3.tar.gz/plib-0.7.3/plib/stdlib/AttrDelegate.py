#!/usr/bin/env python
"""
Module AttrDelegate
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the AttrDelegate class.
"""


class AttrDelegate(object):
    """Delegate attribute access to an underlying object.
    """
    
    def __init__(self, obj):
        self._o = obj
    
    def __getattr__(self, name):
        # Delegate to the underlying object
        return getattr(self._o, name)
