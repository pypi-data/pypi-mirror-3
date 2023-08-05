#!/usr/bin/env python
"""
Module basecontainer
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the basecontainer class.
"""

from plib.stdlib import AbstractContainerMixin, abstractcontainer


class basecontainer(AbstractContainerMixin, abstractcontainer):
    """Base class for immutable container.
    
    An abstract class to provide the minimal possible support of the
    Python container protocol. Subclasses can implement just the __len__
    and _get_data methods to allow the class to be used in the standard
    Python container idioms like for item in container, etc. This
    container is immutable, so its length and its items cannot be
    changed (increasing levels of mutability are provided by the
    basesequence and baselist classes); note that this does
    *not* mean the underlying data structure must be immutable, only
    that the view of it provided by this container class is.
    """
    pass
