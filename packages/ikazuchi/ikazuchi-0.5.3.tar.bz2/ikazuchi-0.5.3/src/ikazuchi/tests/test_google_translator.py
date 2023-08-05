# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.translator import TranslatingGoogle

class TestGoogleTranslator(object):

    def setup(self):
        self.t = TranslatingGoogle("ja", "en", None)

    def test_get_url(self):
        def detect(): pass

        expected = "https://www.googleapis.com/language/translate/v2/detect"
        assert_equal(expected, self.t.get_url(detect))

    def test_detect(self):
        res = self.t.detect([unicode("テスト", "utf-8")])
        assert_equal(u"ja", res[1][0][0][u"language"])

    def test_translate(self):
        assert_equal(('Google', [u'Test']),
                     self.t.translate([unicode("テスト", "utf-8")]))
