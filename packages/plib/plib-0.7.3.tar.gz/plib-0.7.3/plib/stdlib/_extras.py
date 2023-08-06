#!/usr/bin/env python
"""
Module _EXTRAS -- Enhancing the builtin namespace
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from __future__ import generators # to ensure we can use yield in version 2.2

import sys
from operator import mul as _mul


def first(iterable, default=None):
    """Return first item in iterable, or default if empty.
    """
    for item in iterable:
        return item
    return default


if sys.version_info < (2, 4):
    
    def inverted(mapping, keylist=None):
        """Return a mapping that is the inverse of the given mapping.
        
        The optional argument ``keylist`` limits the keys that are inverted.
        """
        
        # Can't use generator expressions so we build the generator by hand
        if keylist is not None:
            def generator():
                for key in keylist:
                    yield mapping[key], key
        else:
            def generator():
                for key, value in mapping.iteritems():
                    yield value, key
        return mapping.__class__(generator())


else:
    
    def inverted(mapping, keylist=None):
        """Return a mapping that is the inverse of the given mapping.
        
        The optional argument ``keylist`` limits the keys that are inverted.
        """
        
        if keylist is not None:
            return mapping.__class__((mapping[key], key)
                for key in keylist)
        return mapping.__class__((value, key)
            for key, value in mapping.iteritems())


def last(iterable, default=None):
    """Return last item in iterable, or default if empty.
    """
    result = default
    for item in iterable:
        result = item
    return result


def prod(iterable, mul=_mul):
    """Return the product of all items in iterable.
    """
    return reduce(mul, iterable, 1)
