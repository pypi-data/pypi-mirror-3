# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.translator import TranslatingGoogle

class TestGoogleTranslator(object):
    """
    Do not test to request actually since Google Translate API v2 is
    a paid service from 2011/12/1
    """

    def setup(self):
        self.t = TranslatingGoogle("ja", "en", None)

    def test_get_url(self):
        def detect(): pass

        expected = "https://www.googleapis.com/language/translate/v2/detect"
        assert_equal(expected, self.t.get_url(detect))

    @nottest
    def test_detect(self):
        res = self.t.detect([unicode("テスト", "utf-8")])
        assert_equal(u"ja", res[1][0][0][u"language"])

    @nottest
    def test_translate(self):
        assert_equal(('Google', [u'Test']),
                     self.t.translate([unicode("テスト", "utf-8")]))
