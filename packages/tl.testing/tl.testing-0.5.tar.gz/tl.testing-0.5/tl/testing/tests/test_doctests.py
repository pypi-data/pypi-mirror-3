# Copyright (c) 2008-2011 Thomas Lotze
# See also LICENSE.txt

import doctest
import mock
import os
import os.path
import pkg_resources
import re
import shutil
import sys
import tempfile
import threading
import tl.testing
import tl.testing.cairo
import tl.testing.doctest
import tl.testing.fs
import tl.testing.script
import unittest
import zope.testing.renormalizing


flags = (doctest.ELLIPSIS |
         doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_NDIFF)

checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'[0-9]+\.[0-9]{3}s'), 'N.NNNs'),
    (re.compile(r'Thread\(Thread-[0-9]+, '), 'Thread(Thread-1, '),
    (re.compile(r', started -?[0-9]+\)>'), ', started NNN)>'),
    (re.compile(r', started daemon -?[0-9]+\)>'), ', started daemon NNN)>'),
    (re.compile(r'%s.*-test_dir%s' % (tempfile.gettempdir(), os.sep)),
     '/test_dir/'),
    ])


forever = []
for i in (0, 1):
    lock = threading.Lock()
    lock.acquire()
    forever.append((threading.Condition(), lock))


def wait_forever(i=0):
    condition, lock = forever[i]
    with condition:
        lock.release()
        condition.wait()


def kill_waiting_thread(i=0):
    condition, lock = forever[i]
    lock.acquire()
    with condition:
        condition.notify()


def run(suite):
    unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(suite)


def setup(test):
    tl.testing.fs.setup_sandboxes()
    test.globs.update(
        Mock=mock.Mock,
        run=run,
        wait_forever=wait_forever,
        kill_waiting_thread=kill_waiting_thread,
        )


def teardown(test):
    tl.testing.fs.teardown_sandboxes()
    tl.testing.script.teardown_scripts()


def cairo_setup(test):
    setup(test)
    test.test_dir = tempfile.mkdtemp(suffix='-test_dir')
    test.original_cwd = os.getcwd()
    os.chdir(test.test_dir)

    for name in ['rgb24.png']:
        shutil.copyfile(
            pkg_resources.resource_filename('tl.testing', 'testimages/'+name),
            os.path.join(test.test_dir, name))

    def write(path, text):
        f = open(path, 'w')
        f.write(text)
        f.close()
        return os.path.abspath(path)

    test.globs.update(write=write)

    os.environ.pop('CAIRO_TEST_RESULTS', '')


def cairo_teardown(test):
    os.chdir(test.original_cwd)
    shutil.rmtree(test.test_dir)


def test_suite():
    options = dict(optionflags=flags,
                   checker=checker,
                   setUp=setup,
                   tearDown=teardown,
                   package=tl.testing,
                   )
    doctest_dir = os.path.dirname(tl.testing.__file__)
    testfiles = set(filename
                    for filename in os.listdir(doctest_dir)
                    if filename.endswith('.txt'))
    cairo_testfiles = set(filename for filename in testfiles
                          if filename.startswith('cairo'))

    suite = doctest.DocFileSuite(
        *sorted(testfiles-cairo_testfiles), **options)

    options.update(setUp=cairo_setup, tearDown=cairo_teardown, footnotes=True)
    suite.addTest(tl.testing.doctest.DocFileSuite(
            *sorted(cairo_testfiles), **options))

    suite.addTest(tl.testing.cairo.DocFileSuite('cairo.txt', **options))

    options['footnotes'] = False
    suite.addTest(tl.testing.cairo.DocFileSuite('../../README.txt', **options))

    return suite
