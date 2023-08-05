===========================
The tl.testing distribution
===========================

This package provides various utilities that can be used when writing tests.
It is compatible to Python versions 2.6 and 2.7.


Sandboxes of directories and files
==================================

When testing code that modifies directories and files, it is useful to be able
to create and inspect a sample tree of directories and files easily. The
``tl.testing.fs`` module provides support for creating a tree from a textual
description, listing it in the same format and clean up after itself.

In a doc test, these facilities might be used like this to create and list a
directory, a file and a symbolic link:

>>> from tl.testing.fs import new_sandbox, ls
>>> new_sandbox("""\
... d foo
... f foo/bar asdf
... l baz -> foo/bar
... """)

>>> ls()
l baz -> foo/bar
d foo
f foo/bar asdf

See the file ``fs.txt`` found with the source code for further advice,
including how to set up and tear down tests using file-system sandboxes.


Installing callable scripts
===========================

Some functionality one might want to test makes use of external programs such
as a pager or a text editor. The ``tl.testing.script`` module provides
utilities that install simple mock scripts in places where the code to be
tested will find them. They take a string of Python code and create a wrapper
script that sets the Python path to match that of the test and runs the code.

This is how such a mock script might be used in a doc test:

>>> from tl.testing.script import install
>>> script_path = install("print 'A simple script.'")
>>> print open(script_path).read()
#!...
<BLANKLINE>
import sys
sys.path[:] = [...]
<BLANKLINE>
print 'A simple script.'

>>> import subprocess
>>> sub = subprocess.Popen(script_path, shell=True, stdout=subprocess.PIPE)
>>> stdout, stderr = sub.communicate()
>>> print stdout
A simple script.

See the file ``script.txt`` found with the source code for further
possibilities how to install and access mock scripts as well as how to tear
down tests using mock scripts.


Doc-testing the graphical content of cairo surfaces
===================================================

While it is straight-forward to compare the content of two `cairo`_ surfaces
in Python code, handling graphics is beyond doc tests. However, the `manuel`_
package can be used to extract more general test cases from a text document
while allowing to mix them with doc tests in a natural way.

.. _cairo: http://cairographics.org/pycairo/

.. _manuel: http://pypi.python.org/pypi/manuel

The ``tl.testing.cairo`` module provides a test suite factory that uses manuel
to execute graphical tests formulated as restructured-text figures. The
caption of such a figure is supposed to be a literal Python expression whose
value is a cairo surface, and its image is used as the test expectation.

This is how a surface might be compared to an expected image in a doc test:

::

    >>> import cairo
    >>> from pkg_resources import resource_filename

    >>> image = resource_filename('tl.testing', 'testimages/correct.png')

    .. figure:: tl/testing/testimages/correct.png

        ``cairo.ImageSurface.create_from_png(image)``

See the file ``cairo.txt`` found with the source code for further advice and
documentation of the possible test output.


Working with threads in test code
=================================

The standard ``TestCase`` class doesn't collect errors and failures that
occurred in other threads than the main one. The ``tl.testing.thread`` module
provides thread classes and a ``ThreadAwareTestCase`` class to allow just
that, as well as some other conveniences for tests that deal with threads:
preventing expected unhandled exceptions in threads from being printed with
the test output, reporting threads left behind by a test, running code in a
daemon thread, joining threads and counting the threads started during the
test's run time:

>>> import time
>>> import tl.testing.thread
>>> class SampleTest(tl.testing.thread.ThreadAwareTestCase):
...
...     def test_error_in_thread_should_be_reported(self):
...         with tl.testing.thread.ThreadJoiner(1):
...             self.run_in_thread(lambda: 1/0)
...
...     def test_active_count_should_count_only_new_threads(self):
...         with tl.testing.thread.ThreadJoiner(1):
...             self.run_in_thread(lambda: time.sleep(0.1))
...             self.assertEqual(1, self.active_count())
...         self.assertEqual(0, self.active_count())

>>> import unittest
>>> run(unittest.makeSuite(SampleTest))
======================================================================
ERROR: test_error_in_thread_should_be_reported (__builtin__.SampleTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
ZeroDivisionError: integer division or modulo by zero
----------------------------------------------------------------------
Ran 2 tests in N.NNNs
FAILED (errors=1)

See the file ``thread.txt`` found with the source code for further details of
the ``ThreadAwareTestCase`` class.


Constructing test suites that use manuel
========================================

As ``manuel`` provides some powerful features in addition to standard
doctests, manuel test suites are set up slightly differently from standard
ones. The ``tl.testing.doctest`` module implements a ``DocFileSuite`` factory
that can be used like the standard one but creates a test suite using manuel
and allows some additional configuration related to manuel, among them the
ability to interpret footnotes that used to be done using the deprecated
``zope.testing.doctest``:

>>> sample_txt = write('sample.txt', """\
... [#footnote]_
... >>> x
... 1
...
... .. [#footnote]
...     >>> x = 1
... """)

>>> from tl.testing.doctest import DocFileSuite
>>> run(DocFileSuite(sample_txt, footnotes=True))
----------------------------------------------------------------------
Ran 1 test in N.NNNs
OK

>>> sample_txt = write('sample.txt', """\
... .. code-block:: python
...     x = 1
...
... >>> x
... 1
... """)

>>> import manuel.codeblock
>>> run(DocFileSuite(sample_txt, manuel=manuel.codeblock.Manuel()))
----------------------------------------------------------------------
Ran 1 test in N.NNNs
OK


.. Local Variables:
.. mode: rst
.. End:
