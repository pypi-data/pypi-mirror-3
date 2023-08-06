#!/usr/bin/env python
"""
Module basemapping
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the basekeyed class.
"""

from plib.stdlib import AbstractMappingMixin, abstractmapping


class basemapping(AbstractMappingMixin, abstractmapping):
    """Base class for mapping with fixed keys but mutable values.
    
    An abstract mapping whose keys cannot be changed. Implements
    key checking on item assignment to enforce this restriction.
    
    This class can be used to provide a mapping-like view of data
    structures whose set of keys cannot be changed, but which can
    have keys re-bound to new values.
    
    Note: this class does not implement any mechanism to initialize
    the mapping from another one (i.e., to be able to call the
    constructor with another mapping as an argument, or with keyword
    arguments, as a dict can be). Subclasses that desire such a
    mechanism must implement it with an overridden constructor, and
    must ensure that the mechanism is compatible with the __contains__
    and __setitem__ methods (so that those methods will not raise
    a KeyError during the initialization process).
    """
    pass
