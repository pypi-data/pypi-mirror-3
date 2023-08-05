# Copyright (c) 2009-2012 Thomas Lotze
# See also LICENSE.txt

"""Doc-testing the graphical content of cairo surfaces.

"""

import manuel
import os
import os.path
import re
import sys
import tl.testing.doctest

# XXX The following import is conditional only for the sake of building the
# API docs at <http://tltesting.readthedocs.org/>. Any logic about the absence
# of the cairo C module at RtD should move to the Sphinx configuration asap.
try:
    cairo = manuel.absolute_import('cairo')
except ImportError:
    cairo = object()

doctest = manuel.absolute_import('doctest')

FORMATS = dict((getattr(cairo, attr), 'cairo.'+attr)
               for attr in dir(cairo)
               if 'FORMAT' in attr)


class Test(object):
    """A graphical test that compares a cairo surface with an expected image.

    A test instance represents a test run on one region of a doc-test file.
    The region is identified as being a ReST figure with a caption that is a
    literal expression. The test is characterised by that expression and the
    path to the referenced image.

    The example's Python expression is evaluated in the context of the test
    case's global variables. It is expected to be a cairo Surface. The
    expected graphical content is loaded from the referenced file, which must
    be a PNG image.

    Failures:
        'Exception raised: <traceback>'
            The expression raised an exception when evaluated.
        'Expected a cairo surface, Got: <expression value>'
            The expression's value is not a cairo Surface instance.
        'Image differs from expectation: <path to image>'
            The graphical content of the cairo Surface could be computed but
            does not meet the test's expectation.

    Errors:
        'Could not load expectation: <path to image>'
            The referenced image is not a readable PNG file.

    If the expression could be evaluated to a cairo Surface and the test
    failed or raised an error later, the CAIRO_TEST_RESULTS environment
    variable is consulted. If set, is taken to be the path to an existing
    directory and the surface's content is written to a file in that
    directory. The file name is computed from the path to the expected image.

    """

    start = re.compile(r'^\s*\.\. figure:: (?P<src>\S+)\n\s*\n', re.MULTILINE)

    end = re.compile(r'(#\s*options:(?P<opt>.*))?\n\s*(\n|\Z)', re.MULTILINE)

    @classmethod
    def _caption(cls, region):
        start_len = cls.start.match(region.source).end()
        return region.source[
            start_len:cls.end.search(region.source, start_len).start()]

    @classmethod
    def match(cls, region):
        """Decide whether a region matching by regex really represents a test.

        In order for a region to represent a test, its figure caption must
        contain exactly one literal expression marked up by double back-ticks.

        """
        return cls._caption(region).count('``') == 2

    def __init__(self, document, region):
        self.document = document
        self.region = region
        self.src = region.start_match.group('src')
        self.expression = self._caption(region).split('``')[1]
        self.options = region.end_match.group('opt') or ''
        self.normalisations = [normalise_exclude]

    def evaluate(self, globs):
        """Compute the cairo surface under test and compare it with the image.

        Returns the failure message or None if the test passed.

        """
        try:
            result = eval(self.expression, globs)
        except:
            return 'Exception raised:\n%s' % doctest._indent(
                doctest._exception_traceback(sys.exc_info()))

        if not isinstance(result, cairo.ImageSurface):
            return 'Expected a cairo.ImageSurface\nGot:\n    %s\n' % result

        try:
            options = eval('(lambda **options: options)(%s)' % self.options,
                           globs)
        except Exception:
            raise Exception(
                'Options could not be evaluated in example at line %s:\n%s'
                % (self.region.lineno,
                   doctest._indent(
                        doctest._exception_traceback(sys.exc_info()))))

        base = os.path.dirname(self.document.location)
        path = os.path.join(base, *self.src.split('/'))

        try:
            expected = cairo.ImageSurface.create_from_png(path)
        except Exception:
            raise Exception('Could not load expectation: %s\n' % self.src
                            + self.store_result(result))

        result_format = result.get_format()
        expected_format = expected.get_format()
        if result_format != expected_format:
            return ('ImageSurface format differs from expectation:\n'
                    'Expected: %s\nGot:      %s\n' %
                    (FORMATS[expected_format], FORMATS[result_format]))

        raw_result = result
        if result_format == cairo.FORMAT_RGB24:
            # The buffer has undefined bits, producing false mismatches.
            result = copy_to_ARGB32(result)
            expected = copy_to_ARGB32(expected)

        used_options = set()
        for handler in self.normalisations:
            result, expected, used = handler(result, expected, options)
            used_options.update(used)

        unused_options = set(options) - used_options
        if unused_options:
            raise Exception('Unused options in example at line %s: %s.'
                            % (self.region.lineno,
                               str(sorted(unused_options))[1:-1]))

        if result.get_data() != expected.get_data():
            return ('Image differs from expectation: %s\n' % self.src
                    + self.store_result(raw_result))

    def store_result(self, result):
        """Write the surface's content to a file on failure or error.

        Returns a line of output pointing to the file, or '' if no target
        directory is specified by the environment.

        """
        path = os.environ.get('CAIRO_TEST_RESULTS')
        if not path:
            return ''

        path = os.path.join(path, self.src.replace('/', '-'))
        try:
            result.write_to_png(path)
        except Exception:
            return '(could not write result to %s)\n' % path
        else:
            return '(see %s)\n' % path


def copy_to_ARGB32(surface):
    copy = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, surface.get_width(), surface.get_height())
    ctx = cairo.Context(copy)
    ctx.set_source_surface(surface)
    ctx.paint()
    return copy


def normalise_exclude(result, expected, options):
    for ctx in (cairo.Context(result), cairo.Context(expected)):
        ctx.set_source_rgb(0, 0, 0)
        for item in options.get('exclude', ()):
            ctx.rectangle(*item)
            ctx.fill()
    return result, expected, ['exclude']


class Result(object):
    """The result of a test for a cairo Surface's graphical content.

    A test result is characterised by the failure message, which is an empty
    string if the test passed.

    """

    def __init__(self, test, error):
        self.test = test
        self.error = error
        self.document = test.document
        self.region = test.region

    def format(self):
        """Return a formatted failure message if the test failed.

        """
        if self.error:
            return ('File "%s", line %s, in %s:\n'
                    'Failed example:\n    %s\n%s' %
                    (self.document.location, self.region.lineno,
                     os.path.basename(self.document.location),
                     self.test.expression, self.error))


class Manuel(manuel.Manuel):
    """Manuel test runner that exercises Test and Result implementations.

    """

    def __init__(self, Test, Result):
        self.Test = Test
        self.Result = Result
        super(Manuel, self).__init__(parsers=[self.parse],
                                     evaluaters=[self.evaluate],
                                     formatters=[self.format])

    def parse(self, document):
        """Create Test instances for matching regions of a document.

        """
        for region in document.find_regions(self.Test.start, self.Test.end):
            if self.Test.match(region):
                document.claim_region(region)
                region.parsed = self.Test(document, region)

    def evaluate(self, region, document, globs):
        """Evaluate the region's Test, if any, in the context of globs.

        """
        if region.evaluated:
            return
        test = region.parsed
        if isinstance(test, self.Test):
            region.evaluated = self.Result(test, test.evaluate(globs))

    def format(self, document):
        """Format Results obtained for matching regions of a document.

        """
        for region in document:
            result = region.evaluated
            if isinstance(result, self.Result):
                region.formatted = result.format()


def DocFileSuite(*paths, **options):
    """Return a TestSuite that runs doc-test files with graphical tests.

    Parameters are the same as for tl.testing.doctest.DocFileSuite.

    """
    m = Manuel(Test, Result)
    if 'manuel' in options:
        m += options['manuel']
    options['manuel'] = m
    return tl.testing.doctest.DocFileSuite(*paths, **options)
