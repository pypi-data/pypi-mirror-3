#! /usr/bin/env python
"""
Module CachedMethod
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Decorator class to implement a method whose value for a
given set of arguments is cached so it only has to be
computed once for those arguments. Useful for methods
that are expensive to compute but whose value for a given
set of arguments is invariant.
"""

from functools import wraps

from plib.stdlib.decotools import cached_function


class CachedMethod(object):
    """Decorator class for cached method.
    
    This is a non-data descriptor that wraps a method with
    the ``cached_function`` decorator separately for each
    instance of its class. This allows caching of method
    results by argument separately for each instance, with
    no risk of overlap or of results not being cached because
    the class instance is not hashable.
    """
    
    def __init__(self, func, name=None, doc=None):
        self.__func = func
        self.__name = name or func.__name__
        self.__doc__ = doc or func.__doc__
    
    def __get__(self, instance, cls):
        # Note that for unbound method calls we don't cache,
        # since we have no instance to use to compute the value
        if instance is None:
            return self
        # The only drawback to all this is that the "method"
        # will not be an instance of the "instancemethod" class
        # to Python; but this doesn't appear to cause any problems
        @cached_function
        @wraps(self.__func)
        def _method(*args, **kwargs):
            return self.__func(instance, *args, **kwargs)
        setattr(instance, self.__name, _method)
        return _method
