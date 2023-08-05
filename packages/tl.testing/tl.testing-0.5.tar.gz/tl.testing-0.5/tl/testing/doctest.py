# Copyright (c) 2011 Thomas Lotze
# See also LICENSE.txt

"""Constructing test suites that use manuel.

"""

import manuel
import manuel.doctest
import manuel.footnote
import manuel.testing
import os.path
import unittest

doctest = manuel.absolute_import('doctest')


def DocFileSuite(*paths, **options):
    """Return a TestSuite that runs doc-test files using manuel.

    Parameters that are the same as for Python's standard doctest.TestSuite:
    module_relative, package, setUp, tearDown, globs, optionflags, checker

    footnotes: whether to interpret footnotes

    manuel: optional manuel.Manuel instance with additional behaviour

    """
    suite = unittest.TestSuite()

    m = manuel.doctest.Manuel(optionflags=options.pop('optionflags', 0),
                              checker=options.pop('checker', None))
    if options.pop('footnotes', False):
        m += manuel.footnote.Manuel()
    if 'manuel' in options:
        m += options.pop('manuel')

    relative = options.pop('module_relative', True)
    package = options.pop('package', None)

    for path in sorted(paths):
        if relative and not os.path.isabs(path):
            calling_module = doctest._normalize_module(package)
            path = doctest._module_relative_path(calling_module, path)
        path = os.path.abspath(path)
        try:
            suite.addTest(manuel.testing.TestSuite(m, path, **options))
        except:
            print
            print 'Error: could not parse doctest file', path
            print
            raise

    return suite
