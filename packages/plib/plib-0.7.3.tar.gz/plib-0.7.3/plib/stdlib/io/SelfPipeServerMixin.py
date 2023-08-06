#!/usr/bin/env python
"""
Module SelfPipeServerMixin
Sub-Package STDLIB.IO of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SelfPipeServerMixin`` class,
which provides "drop-in" usage of ``SelfPipe`` for
servers that conform to the PLIB I/O server API. The
``SocketServer`` class in ``plib.stdlib.io.async`` uses
this class to implement the self-pipe trick.
"""

from plib.stdlib import SelfPipe
from plib.stdlib.func import partial


# This will be the callback passed to the self-pipe; we define it
# here so it's visible at module level (among other things, this
# allows the pickler in the multiprocessing module to find it,
# which is necessary for forking to work on Windows)

def sig_callback(self, flag):
    self.terminate_flag = flag


class SelfPipeServerMixin(object):
    """Implements the self-pipe trick for PLIB servers.
    
    Overrides the ``terminate`` method to write a termination signal
    to the pipe. Signal handlers can therefore just call ``terminate``
    to shut down the server (in accordance with the standard semantics
    for that method).
    
    Overrides the ``serve_forever`` method to set up the pipe before
    starting the server loop. The pipe is set up with a callback that
    stores the byte read from the pipe in ``terminate_flag``. Each
    server class that uses this mixin must still set up a method for
    detecting when there is a byte to be read from the pipe (the async
    socket server in this library subclasses the pipe class so it
    will be included in the async polling loop; the blocking server
    includes the pipe's read file descriptor in the select check it
    makes to detect when there is a pending connection to be accepted).
    
    Overrides the ``keep_running`` method to check ``terminate_flag``.
    
    The ``pipe_class`` field stores the class that will be instantiated
    to create the pipe (an example is the async socket server, as
    noted above).
    """
    
    pipe_class = SelfPipe
    
    terminate_flag = None
    terminate_pipe = None
    
    def terminate(self, flag=True):
        # Use self-pipe trick to break out of serve_forever loop.
        
        # Intended use case is to be called from a signal handler (e.g., SIGINT
        # as in the ``SigIntServerMixin`` class). Note that ``flag`` should be
        # one byte long as a string--if not, it will be truncated when it is
        # written to the pipe. Note also that we check to make sure the pipe
        # has been set up (if not, we haven't yet entered the serve_forever
        # loop and we can just set the flag directly).
        
        if self.terminate_pipe is not None:
            self.terminate_pipe.write_sig(flag)
        else:
            self.terminate_flag = flag
    
    def keep_running(self):
        # Override to check the terminate flag
        return super(SelfPipeServerMixin, self).keep_running() and \
            not self.terminate_flag
    
    def serve_forever(self, callback=None):
        # Override to check the terminate flag first, and close down if
        # it is already set (e.g., if user code calls terminate() before
        # this method is entered). Otherwise, set up a callback to check
        # whether the self-pipe has triggered the flag.
        if self.terminate_flag:
            self.close()
        else:
            self.terminate_pipe = self.pipe_class(
                partial(sig_callback, self))
            super(SelfPipeServerMixin, self).serve_forever(callback)
    
    def server_close(self):
        self.terminate_pipe.close()
        super(SelfPipeServerMixin, self).server_close()
