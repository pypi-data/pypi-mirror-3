#!/usr/bin/env python
"""
Module SigChldServerMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SigChldServerMixin`` class, which
specializes ``SigChldMixin`` for servers conforming to the
PLIB I/O server API. The original use case for this class
is as a mixin for the forking ``SocketServer`` class in
``plib.io.blocking``.
"""

from SigChldMixin import SigChldMixin


class SigChldServerMixin(SigChldMixin):
    """Mixin class for PLIB servers to properly reap dead children.
    
    For typical use cases of this class (e.g., mixing in with the
    ``ForkingServer`` class), reaping children inside the SIGCHLD
    handler could be problematic, because it could delay returning
    control to the server loop. Therefore, the ``reap_on_signal`` flag
    is cleared, and the reaping is done in the ``keep_running`` method
    instead. This does not delay reaping because SIGCHLD will break
    the server out of the select system call in its main loop, and
    the ``keep_running`` method will run before the system call is
    restarted.
    """
    
    ignore_sigchld = False
    reap_on_signal = False
    
    def server_start(self):
        # Override to set up the signal handler
        super(SigChldServerMixin, self).server_start()
        self.setup_child_sig_handler()
    
    def _new_child(self, handler, conn, addr):
        child = super(SigChldServerMixin, self)._new_child(
            handler, conn, addr)
        self.track_child(child)
        return child
    
    def start_child(self, handler, conn, addr):
        """Start a new child process and keep track of it.
        
        Note that we call ``reap_children`` here only as a last
        resort safety measure, in case any are missed by the reaping
        in response to the SIGCHLD handler (or in case we're on a
        platform that doesn't have SIGCHLD--see the module docstring
        for ``SigChldMixin``).
        """
        
        self.reap_children()
        super(SigChldServerMixin, self).start_child(handler, conn, addr)
    
    def keep_running(self):
        # Override to reap children before returning
        self.reap_children()
        return super(SigChldServerMixin, self).keep_running()
    
    def server_close(self):
        """Terminate all children when the server closes.
        """
        self.close_children()
        super(SigChldServerMixin, self).server_close()
