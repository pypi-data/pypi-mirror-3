# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

"""Installing callable scripts.

"""

import os
import os.path
import shutil
import sys
import tempfile


HEAD = """\
#!%(executable)s

import sys
sys.path[:] = %(pythonpath)r

"""


original_environ = {}
tmp_paths = []


def install(text, path=None, name=None, on_path=False, env=None):
    """Install a mock Python script that can be called as an external program.

    text
        content of the script without the interpreter (#!...) line
    path
        optional target path (including the script's file name)
    name
        optional script's file name, put it in a temporary directory
    on_path
        whether to make the script available on the binary search path (PATH)
    env
        optional environment variable to store the script path (e.g. PAGER)

    The path to the script is appended to a list of script to remove upon
    tear-down. If environment variables are modified, their original state is
    saved so it may be reset after the test has run.

    Returns the path to the script.

    """
    if path is not None:
        tmp_paths.append(path)
        file_ = open(path, 'w')
    elif name is not None:
        directory = tempfile.mkdtemp()
        tmp_paths.append(directory)
        path = os.path.join(directory, name)
        file_ = open(path, 'w')
    else:
        handle, path = tempfile.mkstemp()
        tmp_paths.append(path)
        file_ = os.fdopen(handle, 'w')

    file_.write(HEAD % dict(
        executable=sys.executable,
        pythonpath=sys.path,
        ))

    file_.write(text)

    file_.close()
    os.chmod(path, 0754)

    if on_path:
        original_environ.setdefault('PATH', os.environ['PATH'])
        os.environ['PATH'] = ':'.join((directory, os.environ['PATH']))

    if env is not None:
        original_environ.setdefault(env, os.environ.get(env))
        os.environ[env] = path

    return path


def teardown_scripts(test=None):
    """Scripts-related test tear-down handler.

    Scripts created by the test are removed on tear-down. The environment is
    reset to its state before the test run.

    """
    for key, value in original_environ.iteritems():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value
    original_environ.clear()

    for path in tmp_paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    del tmp_paths[:]
