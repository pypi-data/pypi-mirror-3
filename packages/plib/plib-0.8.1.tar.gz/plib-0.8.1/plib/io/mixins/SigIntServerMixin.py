#!/usr/bin/env python
"""
Module SigIntServerMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SigIntServerMixin`` class. This
class customizes ``SigIntMixin`` for use with PLIB servers.
It is useful when simple termination signal functionality is
desired without all the extra frills of ``PServerBase``.
"""

from SigIntMixin import SigIntMixin


class SigIntServerMixin(SigIntMixin):
    """Mixin class for PLIB servers to do controlled shutdown on Ctrl-C.
    
    Overrides ``server_start`` to set up the signal handler.
    Sets ``handler_attr`` to point to the ``terminate`` method.
    
    The default of exiting on Ctrl-C (SIGINT) can be changed by
    overriding the ``term_sigs`` class field; it should contain
    a list of signals to be treated as "terminate" signals. See
    the ``PServerBase`` class for an example.
    """
    
    handler_attr = 'terminate'
    
    def server_start(self):
        super(SigIntServerMixin, self).server_start()
        self.setup_term_sig_handler()
