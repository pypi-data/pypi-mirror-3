#!/usr/bin/env python
"""
Module SerialServerMixin
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SerialServerMixin class.
"""

from plib.stdlib.io.serial import BaseServer
from plib.stdlib.io.blocking import ServerMixin


class SerialServerMixin(BaseServer, ServerMixin):
    """Mixin class for blocking server-side serial I/O.
    """
    pass
