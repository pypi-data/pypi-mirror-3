# -*- coding: utf-8 -*-

import sys
from nose.tools import *
from StringIO import StringIO

# functions for test
from ikazuchi.core.handler import *

class TestSingleSentenceHandler(object):

    class Option(object):
        api = "google"
        sentences = [""]
        encoding = ["utf-8", "utf-8"]
        quiet = False
        detect = False

    def setup(self):
        sys.stdout = StringIO()
        self.opts = TestSingleSentenceHandler.Option()

    def _dummy_translate(self, sentence):
        return "", sentence

    def test_with_quiet_option(self):
        self.opts.quiet = True
        h = SingleSentenceHandler(self.opts)
        h._call_method(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal("translate():             ", first_line)

    def test_detect_with_quiet_option(self):
        self.opts.quiet = True
        self.opts.detect = True
        h = SingleSentenceHandler(self.opts)
        h._call_method(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal("detect():                ", first_line)

    def test_without_quiet_option(self):
        h = SingleSentenceHandler(self.opts)
        h._call_method(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal("sentence:                ", first_line)
