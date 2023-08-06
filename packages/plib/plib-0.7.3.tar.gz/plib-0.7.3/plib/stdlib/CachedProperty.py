#! /usr/bin/env python
"""
Module CachedProperty
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Decorator class to implement a property whose value is
cached in the instance dictionary after the first access.
Useful for properties that are expensive to compute but
whose values do not change. The property is read-only.
"""


class CachedProperty(object):
    """Decorator class for cached property.
    
    This class is a non-data descriptor using the Python
    descriptor protocol, which means it is only called
    if the property is not found in the instance
    dictionary. This feature is what lets us cache the
    property result after the first access.
    """
    
    def __init__(self, fget, name=None, doc=None):
        self.__fget = fget
        self.__name = name or fget.__name__
        self.__doc__ = doc or fget.__doc__
    
    def __get__(self, instance, cls):
        # Note that for unbound method calls we don't cache,
        # since we have no instance to use to compute the value
        if instance is None:
            return self
        result = self.__fget(instance)
        setattr(instance, self.__name, result)
        return result
