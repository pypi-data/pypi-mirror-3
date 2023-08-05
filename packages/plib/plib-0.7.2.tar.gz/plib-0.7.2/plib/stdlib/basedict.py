#!/usr/bin/env python
"""
Module basedict
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the basedict class.
"""

from plib.stdlib import AbstractDictMixin, abstractdict


class basedict(AbstractDictMixin, abstractdict):
    """Base class for fully mutable dictionary.
    
    Base dict class that partially implements the necessary abstract methods.
    
    This class reduces the amount of work required to make a data structure
    look like a Python dict. It implements the __getitem__, __setitem__,
    and __delitem__ methods to provide the following:
    
    - checking of keys for __getitem__ and __delitem__;
    
    - distinguishing in __setitem__ between setting the value of an existing
      key, and adding a new key with its value.
    
    The work needed to fully implement a dict-emulator is thus reduced to the
    following: implement _get_value to retrieve one value by key, _set_value
    to store one value by key, _add_key to add a new key with its value, and
    _del_key to remove one key with its value. Implementing these methods is
    sufficient to overlay full dict functionality on the underlying data
    structure. Also, as the ``abstractdict`` docstring states, __init__ will
    almost always need to be overridden to initialize the underlying data
    structure prior to this class's constructor (which populates the data)
    being called.
    
    Note that if no or limited mutability is desired, the basemapping and
    basekeyed classes are designed on the same principles as above, but
    with all mutability (for basekeyed) or all changes to the set of allowed
    keys (for basemapping) disabled.
    """
    pass
