# Copyright (c) 2011-2012 Thomas Lotze
# See also LICENSE.txt

"""Working with threads in test code.

"""

import sys
import threading
import unittest


class ThreadAwareTestCase(unittest.TestCase):
    """TestCase implementation that adds some features for handling threads.

    While the default ``unittest.TestCase`` doesn't concern itself with
    threading at all, this implementation adds the following:

    - interplay with threads such that exceptions and failures that occur in a
      thread get collected along those from the main thread

    - reporting of threads left behind by a test

    - a convenience helper for running code in a daemon thread

    - a convenience helper for counting threads started during the current
      test method's execution

    The ``ThreadAwareTestCase`` is instantiated the same way as
    ``unittest.TestCase``.

    """

    def __init__(self, *args):
        super(ThreadAwareTestCase, self).__init__(*args)
        self.ExceptionReportingThread = ExceptionReportingThread.bind(self)

    def run(self, result=None):
        """Thread-aware wrapper of ``unittest.TestCase.run``; see there.

        .. sphinx-autodoc-skip

        """
        self.result = self.defaultTestResult() if result is None else result
        with ThreadJoiner(0, check_alive=False) as joiner:
            self._before = joiner.before
            result = super(ThreadAwareTestCase, self).run(self.result)
            del self._before
        if joiner.left_behind:
            self.report_threads_left_behind(joiner.left_behind)
        return result

    def active_count(self):
        """Count threads started during the current test method's execution.

        Returns an integer.

        """
        return len(set(threading.enumerate()) - self._before)

    def run_in_thread(self, func, report=True):
        """Run the given function in a daemon thread that handles exceptions.

        Using this thread helper is necessary in order for the thread to play
        with ``ThreadAwareTestCase``'s reporting of errors and failures that
        occurred in threads.

        Passing a false value for the ``report`` option causes unhandled
        exceptions in the thread to be swallowed instead of reported. This
        prevents them from appearing in the middle of more interesting test
        output in the case that they are of no concern themselves.

        This method starts the thread in daemon mode and blocks until the
        thread has actually started executing.

        Returns the thread object.

        """
        factory = (self.ExceptionReportingThread if report
                   else ExceptionSilencingThread)
        thread = factory(target=func)
        thread.daemon = True
        thread.start()
        return thread

    def format_report_on_threads_left_behind(self, threads):
        """Formatting hook for the report on threads left behind by a test.

        Represent the collection of threads passed to this method as a piece
        of text useful to a human who operates the test runner. The output of
        this method is used by the default implementation of the reporting
        hook, ``report_threads_left_behind``.

        Returns a multi-line string.

        """
        return (u'\nThe following test left new threads behind:\n  %s\n'
                u'New thread(s):\n%s\n' % (
                self.id(), '\n'.join('  %r' % thread for thread in threads)))

    def report_threads_left_behind(self, threads):
        """Hook reporting threads left behind by a test to the test runner.

        This hook is meant to do whatever the test runner being used needs to
        be done to display information on the collection of threads passed to
        this hook. The default implementation is meant for a console test
        runner: it formats the threads as a piece of text using the
        ``format_report_on_threads_left_behind`` hook and prints that to
        standard output.

        """
        msg = self.format_report_on_threads_left_behind(threads)
        sys.stdout.write(msg)


class _ExceptionHandlingThread(threading.Thread):
    """Base class of any threads that need their own run method.

    .. sphinx-autodoc-skip

    """

    def start(self):
        """Reporting-aware re-implementation of ``Thread.start``.

        .. sphinx-autodoc-skip

        """
        run = self.run
        self.started = threading.Event()
        try:
            self.run = self._run
            super(_ExceptionHandlingThread, self).start()
            self.started.wait(1)
            if not self.started.is_set():
                raise RuntimeError('Time-out waiting for thread to start.')
        finally:
            self.run = run


class ExceptionReportingThread(_ExceptionHandlingThread):
    """Thread implementation which reports exceptions to a test result object.

    The reporting-thread class is not useful if instantiated directly; it must
    be bound to an instance of the ``ThreadAwareTestCase`` first. It gets thus
    access to the test result object, to which it will report if an exception
    occurs in the thread's business code. An ``AssertionError`` will be
    reported as a test failure, any other exception will be reported as a test
    error.

    """

    _test = None

    def _run(self):
        self.started.set()
        try:
            super(ExceptionReportingThread, self).run()
        except AssertionError:
            self._test.result.addFailure(self._test, sys.exc_info())
        except Exception:
            self._test.result.addError(self._test, sys.exc_info())

    @classmethod
    def bind(cls, test):
        """Bind the class to a specific test.

        Binding the reporting-thread class to a test is necessary for
        instances of it to be able to report errors and failures to the test
        result.

        Returns a subclass of the reporting-thread class.

        """

        class ExceptionReportingThread(cls):
            pass

        ExceptionReportingThread._test = test
        return ExceptionReportingThread


class ExceptionSilencingThread(_ExceptionHandlingThread):
    """Thread implementation which swallows unhandled exceptions.

    Swallowing exceptions is useful if it is clear that they are of no
    interest and shall not mix with more useful test output.

    """

    def _run(self):
        self.started.set()
        try:
            super(ExceptionSilencingThread, self).run()
        except Exception:
            pass


class ThreadJoiner(object):
    """Context manager that tries to join any threads started by its suite.

    This context manager is instantiated with a mandatory ``timeout``
    parameter and an optional ``check_alive`` switch. The time-out is applied
    when joining each of the new threads started while executing the context
    manager's code suite. If ``check_alive`` has a true value (the default),
    a ``RuntimeError`` is raised if a thread is still alive after the attempt
    to join timed out.

    Returns an instance of itself upon entering. This instance has a
    ``before`` attribute that is a collection of all threads active when the
    manager was entered. After the manager exited, the instance has another
    attribute, ``left_behind``, that is a collection of any threads that could
    not be joined within the time-out period. The latter is obviously only
    useful if ``check_alive`` is set to a false value.

    """

    def __init__(self, timeout, check_alive=True):
        self.timeout = timeout
        self.check_alive = check_alive

    def __enter__(self):
        self.before = set(threading.enumerate())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for thread in set(threading.enumerate()) - self.before:
            thread.join(self.timeout)
            if self.check_alive and thread.is_alive():
                raise RuntimeError('Timeout joining thread %r' % thread)
        self.left_behind = sorted(
            set(threading.enumerate()) - self.before, key=lambda t: t.name)
