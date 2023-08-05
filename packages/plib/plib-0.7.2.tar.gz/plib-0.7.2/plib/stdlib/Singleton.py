#!/usr/bin/env python
"""
Module Singleton
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Singleton class.
"""


class Singleton(object):
    """Each subclass of this class can have only a single instance.
    
    (Taken from Guido's new-style class intro essay.)
    """
    
    def __new__(cls, *args, **kwds):
        """Only create an instance if it isn't already there.
        """
        
        inst = cls.__dict__.get("__inst__")
        if inst is None:
            cls.__inst__ = inst = object.__new__(cls)
            inst._init(*args, **kwds)
        return inst
    
    def _init(self, *args, **kwds):
        """Override this to do customized initialization.
        
        (This method will only be called once, whereas __init__ will
        be called each time the class constructor is called).
        """
        pass
