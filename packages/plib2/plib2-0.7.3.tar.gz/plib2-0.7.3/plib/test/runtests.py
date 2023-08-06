#! /usr/bin/env python
"""
RUNTESTS.PY -- standard test script
Copyright (C) 2008-2012 by Peter A. Donis

Released under the Python Software Foundation License

Boilerplate test running script. Looks for
the following test files in the directory
of the script file:

- test_*.txt files are run as doctests
- test_*.py files are run as unit tests

Also looks at the ``modules_with_doctests`` global
for the names of Python modules that have doctests
in them.
"""

import sys
import os
import glob
import doctest
import unittest

modules_with_doctests = [
    'plib.stdlib.decotools',
    'plib.stdlib.iters',
    'plib.stdlib._typed_namedtuple'
]

try:
    from collections import defaultdict
except ImportError:
    modules_with_doctests.append('plib.stdlib._defaultdict')

try:
    from functools import namedtuple
except ImportError:
    modules_with_doctests.append('plib.stdlib._namedtuple')

module_relative = False
verbosity = 0


def run_tests():
    doctests = glob.glob("test_*.txt")
    if doctests:
        print "Running doctests..."
        for filename in doctests:
            doctest.testfile(filename, module_relative=module_relative)
    else:
        print "No doctests found."
    if modules_with_doctests:
        print "Running doctests from modules..."
        from plib.stdlib.imp import dotted_import
        for modname in modules_with_doctests:
            mod = dotted_import(modname)
            doctest.testmod(mod)
    else:
        print "No modules with doctests found."
    unittests = [os.path.splitext(os.path.basename(filename))[0]
        for filename in glob.glob("test_*.py")]
    if unittests:
        print "Running unittests..."
        loader = unittest.defaultTestLoader
        # Yes, this is a roundabout way of doing it, but we want
        # to exactly duplicate what would be done if we ran each
        # module individually as a unittest (i.e., running
        # unittest.main() from the module itself); otherwise,
        # particularly with the I/O tests, we can get errors
        # from one test stepping on another
        suites = [loader.loadTestsFromName(modname)
            for modname in unittests]
        fullsuite = unittest.TestSuite(suites)
        runner = unittest.TextTestRunner(verbosity=verbosity)
        runner.run(fullsuite)
    else:
        print "No unittests found."


if __name__ == '__main__':
    # TODO: set module_relative and verbosity from command line options
    run_tests()
