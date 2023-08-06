#!/usr/bin/env python
"""
Module abstractmapping
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the abstractmapping class.
"""

from plib.stdlib import abstractkeyed


class abstractmapping(abstractkeyed):
    """Abstract mapping with fixed keys but mutable values.
    
    An abstract mapping whose keys cannot be changed.
    
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
    
    def __setitem__(self, key, value):
        """Set the value corresponding to key.
        
        Raise ``KeyError`` if ``key`` is not in the list of allowed keys.
        (Note that this requirement no longer holds for the derived
        class ``abstractdict``. See the source for that class.)
        """
        raise NotImplementedError
    
    def update(self, other=None, **kwargs):
        # Note that we depend on __setitem__ to know whether keys not
        # already in the mapping should be allowed (no in this class,
        # yes in abstractdict)
        for mapping in (other, kwargs):
            # Make progressively weaker assumptions about mapping
            if mapping:
                if hasattr(mapping, 'iteritems'):  # saves memory and lookups
                    for k, v in mapping.iteritems():
                        self[k] = v
                elif hasattr(mapping, 'keys'):
                    for k in mapping.keys():
                        self[k] = mapping[k]
                else:
                    for k, v in mapping:
                        self[k] = v
