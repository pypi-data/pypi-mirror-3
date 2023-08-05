# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.translator import BaseTranslator
from ikazuchi.core.translator.utils import *

class TestTranslator(object):

    def setup(self):
        class DummyTranslator(BaseTranslator):
            def __init__(self, lang_from, lang_to, handler): pass

            def detect(self, text): pass

            def translate(self, text): pass

        self.t = DummyTranslator("en", "ja", None)

    def test_parse_html_with_one_span(self):
        html = '<html>この<span class="notranslate">string</span>'\
               'は翻訳されません。</html>'
        actual = self.t.parse_html(unicode(html, "utf-8")).encode("utf-8")
        expected = "この string は翻訳されません。"
        assert_equal(expected, actual)

    def test_parse_html_with_two_span(self):
        html = '<html>この<span class="notranslate">string</span>'\
               'は<span class="notranslate">translate</span></html>'
        expected = "この string は translate"
        actual = self.t.parse_html(unicode(html, "utf-8")).encode("utf-8")
        assert_equal(expected, actual)

    def test_parse_html_with_various(self):
        html = '<html>この<span class="notranslate">string</span>'\
               'は<p>テスト</p>のためで<span>regexp</span>の'\
               'マッチングが<span class="notranslate">correct</span>か'\
               'どうかを<strong>調べます</strong>。</html>'
        expected = "この string は テストのためでregexpの"\
                   "マッチングが correct かどうかを調べます。"
        actual = self.t.parse_html(unicode(html, "utf-8")).encode("utf-8")
        assert_equal(expected, actual)

def test_call_api_with_multithread():
    def dummy_func(num):
        sleep(0.1)
        return num
    from time import sleep
    args = range(1, 30)
    assert_equal(args, call_api_with_multithread(dummy_func, args))
