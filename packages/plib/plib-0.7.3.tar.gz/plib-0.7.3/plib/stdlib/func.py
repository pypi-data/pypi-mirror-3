#!/usr/bin/env python
"""
Module FUNC -- Tools for Functional Programming
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

The ``functools`` module was added to Python in version
2.5, but its functionality is useful in earlier versions
as well. This module is equivalent to ``functools`` for
Python versions where that module is present, and it
provides equivalent implementations of the same functions
for earlier Python versions. Thus, you can say::

    from plib.stdlib import func

and have the functionality available regardless of your
Python version.
"""

try:
    from functools import *

except (ImportError, NameError):
    
    from __builtin__ import reduce
    
    WRAPPER_ASSIGNMENTS = ['__name__', '__module__', '__doc__']
    
    WRAPPER_UPDATES = ['__dict__']
    
    
    def update_wrapper(wrapper, wrapped,
                       assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES):
        """Update wrapper's attributes from wrapped.
        """
        for attr in assigned:
            setattr(wrapper, attr, getattr(wrapped, attr))
        for attr in updated:
            # Need the default empty dict in case wrapped is a builtin and doesn't
            # have a __dict__
            getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    
    
    def wraps(wrapped,
              assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES):
        """Updated decorator with attributes from decorated function.
        """
        def decorator(wrapper):
            update_wrapper(wrapper, wrapped, assigned, updated)
            return wrapper
        return decorator
    
    
    class partial(object):
        """Form partial closure of callable object.
        """
        
        assigned=WRAPPER_ASSIGNMENTS
        updated=WRAPPER_UPDATES
        
        def __init__(self, func, *fargs, **fkwargs):
            self.func = func
            self.args = fargs
            self.keywords = fkwargs
            update_wrapper(self, func, self.assigned, self.updated)
        
        def __call__(self, *args, **kwargs):
            newargs = self.args + args
            newkwargs = self.keywords.copy()
            newkwargs.update(kwargs)
            return self.func(*newargs, **newkwargs)
