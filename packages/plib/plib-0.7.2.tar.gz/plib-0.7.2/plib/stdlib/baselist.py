#!/usr/bin/env python
"""
Module baselist
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the baselist class.
"""

from plib.stdlib import AbstractListMixin, abstractlist


class baselist(AbstractListMixin, abstractlist):
    """Base class for fully mutable abstract list.
    
    Base list class that partially implements the necessary abstract methods.
    
    This class reduces the amount of work required to make a data structure
    look like a Python list. It implements the __getitem__, __setitem__,
    and __delitem__ methods to provide the following:
    
    - normalization of indexes (negative indexes relative to end of list and
      out of range exceptions);
    
    - support for slices as arguments.
    
    The work needed to fully implement a list-emulator is thus reduced to the
    following: implement _get_data to retrieve one item by index, _set_data
    to store one item by index, _add_data to add/insert one item by index,
    and _del_data to remove one item by index. Implementing these methods is
    sufficient to overlay full list functionality on the underlying data
    structure; operations which add, set, or remove multiple items will
    result in multiple calls to _set, _add, or _del as appropriate. Other
    methods can be overridden if needed for efficiency (e.g., to increase
    speed for multi-item operations), per the abstractlist class docstring
    (note that, as that docstring states, __init__ will almost always need
    to be overridden to initialize the underlying data structure, and sort
    must be implemented if sorting functionality is desired).
    
    Note that if no or limited mutability is desired, the basecontainer and
    basesequence classes are designed on the same principles as above, but
    with all mutability (for basecontainer) or all changes in sequence length
    (for basesequence) disabled.
    """
    pass
