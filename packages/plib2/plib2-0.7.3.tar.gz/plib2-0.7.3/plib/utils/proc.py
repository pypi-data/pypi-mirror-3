#!/usr/bin/env python
"""
Module PROC -- Process-Related Utilities
Sub-Package UTILS of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module is for useful process-related functions. Currently
the only function implemented is ``process_output``, which
runs an external process and returns its output as a string.
"""

try:
    from subprocess import Popen, PIPE
    from shlex import split
    
    
    def _get_pipe(cmdline):
        return Popen(split(cmdline), stdout=PIPE).stdout


except ImportError:
    from os import popen
    
    
    def _get_pipe(cmdline):
        return popen(cmdline)
    
    
def process_output(cmdline):
    s = ""
    p = _get_pipe(cmdline)
    try:
        s = p.read()
    finally:
        p.close()
    return s
