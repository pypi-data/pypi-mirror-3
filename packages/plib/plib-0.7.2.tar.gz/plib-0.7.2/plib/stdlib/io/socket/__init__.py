#!/usr/bin/env python
"""
Sub-Package STDLIB.IO.SOCKET of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package includes classes for handling socket
I/O channels. See the docstring for the parent package,
``plib.stdlib.io``, for information on how this package
fits into the overall I/O package structure.
"""

from plib.utils import ModuleProxy

from _socket import *

excludes = ['_socket']

ModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals(),
    excludes=excludes)

# Now clean up our namespace
del ModuleProxy
