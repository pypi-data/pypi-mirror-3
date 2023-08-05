#!/usr/bin/env python
"""
Module PersistentMixin
Sub-Package STDLIB.IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous PersistentMixin class.
"""

from plib.stdlib.io.async import AsyncCommunicator
from plib.stdlib.io.comm import PersistentCommunicator


class PersistentMixin(AsyncCommunicator, PersistentCommunicator):
    pass
