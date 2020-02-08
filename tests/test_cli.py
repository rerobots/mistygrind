"""Basic tests of the command-line interface (CLI)


SCL <scott@rerobots.net>
Copyright (c) 2020 rerobots, Inc.
"""
from io import StringIO
import sys

import mistygrind
from mistygrind import cli


def test_version():
    original_stdout = sys.stdout
    sys.stdout = StringIO()
    cli.main(['-V'])
    res = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert mistygrind.__version__ == res
