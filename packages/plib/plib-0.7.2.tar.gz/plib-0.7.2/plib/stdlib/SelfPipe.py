#!/usr/bin/env python
"""
Module SelfPipe
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SelfPipe`` class, which implements
the self-pipe trick in a general way that can be used by any
application wanting to multiplex socket I/O with signals.
"""

from os import name as os_name


# First the basic API as an abstract base class

class _SelfPipeBase(object):
    """Implements the mechanics of the self-pipe trick.
    
    Two methods are provided for writing to the pipe:
    
    - ``write_pipe``: writes a byte to the pipe.
    
    - ``write_sig``: writes a byte representing a signal to
      the pipe; intended for use inside signal handlers.
    
    Must be instantiated with a callback function that will
    be called with the byte read from the pipe.
    """
    
    written = False
    
    def __init__(self, callback):
        self.callback = callback
        self._init()
    
    def write_sig(self, sig):
        """Convenience method to write a byte representing a signal.
        
        Assumes ``sig`` is an integer that will fit in one byte. If
        it isn't, a byte value of 255 will be written instead.
        """
        
        try:
            b = chr(sig)
        except ValueError:
            b = chr(255)
        self.write_pipe(b)
    
    def write_pipe(self, b):
        """Write byte ``b`` to the pipe.
        
        If ``b`` is more than one byte long, it will be truncated
        prior to writing to the pipe. This is to ensure that the
        ``read_pipe`` can count on reading a single byte each time
        it is called.
        
        We wrap the call with the ``written`` flag to ensure that
        we don't write again until ``read_pipe`` is called to clear
        the pipe. For the intended use case (signaling termination
        to a server), this is not an issue since multiple signals
        are equivalent to one.
        """
        
        if not self.written:
            self._write(str(b)[0])
            self.written = True
    
    def read_pipe(self):
        """Read a byte from the pipe and send it to the callback.
        
        The callback mechanism here keeps everything general,
        so it can be adapted to a variety of use cases.
        """
        
        self.callback(self._read())
        self.written = False
    
    # Abstract methods to be overridden
    
    def _init(self):
        """Initialize the pipe.
        """
        raise NotImplementedError
    
    def fileno(self):
        """Return the file descriptor to select for pipe readability.
        """
        raise NotImplementedError
    
    def _write(self, b):
        """Write a byte to the pipe.
        """
        raise NotImplementedError
    
    def _read(self):
        """Read a byte from the pipe and return it.
        """
        raise NotImplementedError
    
    def close(self):
        """Close the pipe.
        """
        raise NotImplementedError


if os_name == "posix":
    # We're on a Unix-type system and can use os.pipe with select
    
    import os
    
    
    class SelfPipe(_SelfPipeBase):
        
        def _init(self):
            self.fd_read, self.fd_write = os.pipe()
        
        def fileno(self):
            return self.fd_read
        
        def _write(self, b):
            os.write(self.fd_write, b)
        
        def _read(self):
            return os.read(self.fd_read, 1)
        
        def close(self):
            for fd in (self.fd_write, self.fd_read):
                os.close(fd)


else:
    # We're on Windows and have to use an (emulated) socketpair to
    # emulate a select-able pipe
    
    from plib.stdlib.func import partial
    
    from plib.utils._threadwrapper import ThreadWrapper
    from plib.utils._socketwrapper import socketpair_wrapper
    
    
    def _pipe(self, wsock):
        # Just copy the socket to self and exit
        self.wsock = wsock
    
    
    class SelfPipe(_SelfPipeBase):
        
        def _init(self):
            self.rsock, child = socketpair_wrapper(
                partial(_pipe, self), ThreadWrapper)
            # Once this returns, self.wsock will be filled in
            child.wait()
        
        def fileno(self):
            return self.rsock.fileno()
        
        def _write(self, b):
            self.wsock.sendall(b)
        
        def _read(self):
            return self.rsock.recv(1)
        
        def close(self):
            for sock in (self.wsock, self.rsock):
                sock.close()
