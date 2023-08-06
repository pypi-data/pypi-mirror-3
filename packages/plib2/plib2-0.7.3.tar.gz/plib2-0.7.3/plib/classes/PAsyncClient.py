#!/usr/bin/env python
"""
Module PAsyncClient
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PAsyncClient`` class. This is an
asynchronous socket I/O client using the ``PClientBase``
interface.
"""

from plib.classes import PClientBase
from plib.stdlib.io.async import SocketClient


class PAsyncClient(PClientBase, SocketClient):
    """Asynchronous TCP client class.
    
    Connects with TCP server, writes data, and stores the
    result. See the ``PClientBase`` docstring for more
    information.
    """
    pass
