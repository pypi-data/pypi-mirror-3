#!/usr/bin/env python
"""
Module ThreadingServer
Sub-Package STDLIB.IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``ThreadingServer`` class, which
is a threading version of the blocking I/O socket server.
See the module docstring for the base class, ``SocketServer``,
for more information.
"""

from plib.utils._threadwrapper import ThreadWrapper

from plib.stdlib.io import ChildWrapperMixin
from plib.stdlib.io.blocking import SocketServer


class ThreadingServer(ChildWrapperMixin, SocketServer):
    """Threading TCP server.
    
    This server creates a new thread to handle each request.
    """
    
    wrapper_class = ThreadWrapper
