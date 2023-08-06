#!/usr/bin/python -u
"""
Setup script for PLIB package
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib import __version__

__progname__ = "plib2"
__dev_status__ = "Alpha"
__description__ = "A namespace package for a number of useful sub-packages and modules."
__start_line__ = 5
__end_line__ = "The Zen of PLIB"
__license__ = "GNU GPL"
__author__ = "Peter A. Donis"
__author_email__ = "peterdonis@alum.mit.edu"
__ext_names__ = ['plib.extensions._extensions']
__rootfiles__ = ["CHANGES", "LICENSE", "TODO"]
__post_install__ = list("%s-setup-%s.py" % ("plib", s) for s in ("paths", "examples", "gui"))
# NOTE: We use list() here instead of a list comprehension so the 's' variable doesn't leak into globals() below

__classifiers__ = """
Environment :: Console
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: X11 Applications :: GTK
Environment :: X11 Applications :: KDE
Environment :: X11 Applications :: Qt
Intended Audience :: Developers
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

if __name__ == '__main__':
    from SetupHelper import setup_main
    setup_main(globals())
