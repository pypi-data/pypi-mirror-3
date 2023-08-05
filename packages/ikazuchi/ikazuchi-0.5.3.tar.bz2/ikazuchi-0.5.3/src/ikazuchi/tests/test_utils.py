# -*- coding: utf-8 -*-

import sys
from nose.tools import *
from StringIO import StringIO

# functions for test
import ikazuchi.utils


def test_encoding_action():
    class Namespace(object):
        encoding = None
    namespace = Namespace()
    a = ikazuchi.utils.EncodingAction(['-e', '--encoding'], dest='encoding')
    a(None, namespace, "utf-8", None)
    assert_equal(["utf-8", "utf-8"], namespace.encoding)
    a(None, namespace, "utf-8, euc-jp", None)
    assert_equal(["utf-8", "euc-jp"], namespace.encoding)

def test_check_encoding():
    errs = ikazuchi.utils.check_encoding(["euc-jp", "utf-8"])
    assert_equals([], errs)
    errs = ikazuchi.utils.check_encoding(["unknown", "utf-8"])
    assert_equals(["unknown"], errs)
    errs = ikazuchi.utils.check_encoding(["utf-8", "unknown"])
    assert_equals(["unknown"], errs)
    errs = ikazuchi.utils.check_encoding(["unknown", "notexist"])
    assert_equals(["unknown", "notexist"], errs)

def test_get_command():
    import platform
    os_name = platform.system()
    if os_name == "Windows":
        # FIXME: tell me appropriate command
        pass
    else:
        assert_equal(["/bin/ls"], list(ikazuchi.utils.get_command("ls")))

def test_python_version():
    data = [(2, 6, 4, 'final', 0), (2, 5, 1, 'final', 0)]
    sys.stdout = StringIO()
    for ver in data:
        sys.version_info = ver
        try:
            ikazuchi.utils.check_python_version()
            assert_equals("", sys.stdout.getvalue())
        except SystemExit:
            assert_equals(ikazuchi.utils._UNSUPPORTED_VERSION,
                            sys.stdout.getvalue().rstrip('\r\n'))
