#!/usr/bin/env python
"""
Module IMP -- Import Helper Functions
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the following two helper functions for
importing objects:

function dotted_import -- wraps the __import__ builtin so that it
    returns the 'innermost' module in a dotted name; the equivalent
    of 'import x.y.z'

function dotted_from_import -- dotted_import, plus a getattr call to
    retrieve the named attribute from the dotted module; the equivalent
    of 'from x.y.z import a' (except that module a of package x.y.z
    will not be returned unless it has already been imported into the
    namespace of x.y.z)
"""


def dotted_import(name):
    """Return the module pointed to by import x.y.z.
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def dotted_from_import(modname, attrname):
    """Return the module attribute pointed to by from x.y.z import a.
    """
    return getattr(dotted_import(modname), attrname)
