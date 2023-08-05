# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

"""Sandboxes of directories and files.

"""

import os
import os.path
import shutil
import tempfile


original_cwd = None
sandboxes = []


def new_sandbox(specification):
    """Create a directory with items given as lines of text, and chdir to it.

    The specification is a multi-line string each of whose lines takes one of
    the following forms:

    ``d foo``
        create a directory named foo
    ``f foo/bar asdf``
        create a file named bar inside foo/ with content 'asdf'
    ``l baz -> foo/bar``
        create a symbolic link named baz, pointing to foo/bar

    The sandbox directory will be added to the known sandboxes so it can be
    removed when the test setup is torn down.

    """
    root = tempfile.mkdtemp()
    sandboxes.append(root)
    root = os.path.join(root, '')
    for line in specification.splitlines():
        type_, raw_path, comment = (line.split(None, 2) + [''])[:3]
        path = os.path.normpath(os.path.join(root, raw_path))
        if not path.startswith(root):
            raise ValueError('"%s" points outside the sandbox.' % raw_path)
        if type_ == 'f':
            f = open(path, 'w')
            f.write(comment)
            f.close()
        elif type_ == 'd':
            os.mkdir(path)
        elif type_ == 'l':
            assert comment.startswith('-> ')
            os.symlink(comment[3:], path)
    os.chdir(root)


def ls():
    """Print text lines listing the current working directory recursively.

    The format of the text lines is the same as read by the ``new_sandbox()``
    function. Lines are printed in alphabetical order.

    """
    root = os.path.join(os.getcwd(), '')
    items = []

    def handle_symlink(path):
        if os.path.islink(path):
            items.append((path, 'l', '-> ' + os.readlink(path)))
            return True
        return False

    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames:
            path = os.path.join(dirpath, name)
            if not handle_symlink(path):
                items.append((path, 'd', ''))
        for name in filenames:
            path = os.path.join(dirpath, name)
            if not handle_symlink(path):
                items.append((path, 'f', open(path).read()))

    for path, type_, comment in sorted(items):
        assert path.startswith(root)
        print type_, path[len(root):], comment


def setup_sandboxes(test=None):
    """Sandbox-related test set-up handler.

    As creating a sandbox changes the current working directory to it, the
    original working directory is saved by the test setup so it may be
    restored upon tear-down.

    """
    global original_cwd
    original_cwd = os.getcwd()


def teardown_sandboxes(test=None):
    """Sandbox-related test tear-down handler.

    Sandboxes created by the test are removed and the working directory is
    changed back to the current one before the test.

    """
    for path in sandboxes:
        shutil.rmtree(path, ignore_errors=True)
    del sandboxes[:]
    os.chdir(original_cwd)
