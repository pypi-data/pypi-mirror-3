# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.translator import TranslatingMicrosoft

class TestMicrosoftTranslator(object):

    def setup(self):
        self.t = TranslatingMicrosoft("ja", "en", None)

    def test_get_api_path(self):
        def break_sentences(): pass

        def get_language_names(): pass

        assert_equal("BreakSentences?", self.t.get_api_path(break_sentences))
        assert_equal("GetLanguageNames?",
                     self.t.get_api_path(get_language_names))

    def test_break_sentences(self):
        assert_equal(('Microsoft', ['10', '5']),
                     self.t.break_sentences("ikazuchi. test."))

    def test_detect(self):
        assert_equal(('Microsoft', 'ja'),
                     self.t.detect(unicode("テスト", "utf-8")))

    def test_detect_array(self):
        texts = [
            u"ikazuchi",
            u"bonjour",
            unicode("テスト", "utf-8"),
            unicode("你好", "utf-8"),
        ]
        assert_equal(('Microsoft', ['en', 'fr', 'ja', 'zh-CHS']),
                     self.t.detect_array(texts))

    def test_get_language_names(self):
        lang_codes = ["en", "fr", "ja", "zh-CN"]
        assert_equal(('Microsoft', ['English', 'French', 'Japanese',
                        "Chinese Simplified (People's Republic of China)"]),
                     self.t.get_language_names(lang_codes))

    def test_get_languages_for_speak(self):
        assert_equal(
            ('Microsoft', ['ca', 'ca-es', 'da', 'da-dk', 'de', 'de-de',
                'en', 'en-au', 'en-ca', 'en-gb', 'en-in', 'en-us', 'es',
                'es-es', 'es-mx', 'fi', 'fi-fi', 'fr', 'fr-ca', 'fr-fr',
                'it', 'it-it', 'ja', 'ja-jp', 'ko', 'ko-kr', 'nb-no', 'nl',
                'nl-nl', 'no', 'pl', 'pl-pl', 'pt', 'pt-br', 'pt-pt', 'ru',
                'ru-ru', 'sv', 'sv-se', 'zh-chs', 'zh-cht', 'zh-cn',
                'zh-hk', 'zh-tw']),
            self.t.get_languages_for_speak())

    def test_get_languages_for_translate(self):
        assert_equal(
            ('Microsoft', ['ar', 'bg', 'ca', 'zh-CHS', 'zh-CHT', 'cs', 'da',
                'nl', 'en', 'et', 'fi', 'fr', 'de', 'el', 'ht', 'he', 'hi',
                'hu', 'id', 'it', 'ja', 'ko', 'lv', 'lt', 'no', 'pl', 'pt',
                'ro', 'ru', 'sk', 'sl', 'es', 'sv', 'th', 'tr', 'uk', 'vi']),
            self.t.get_languages_for_translate())

    def test_translate(self):
        assert_equal(('Microsoft', 'Test'),
                     self.t.translate(unicode("テスト", "utf-8")))

    def test_translate_array(self):
        texts = [
            unicode("テスト", "utf-8"),
            unicode("ペンギン", "utf-8"),
            unicode("鉛筆", "utf-8"),
        ]
        assert_equal(('Microsoft', ['Test', 'Penguin', 'Pencil']),
                     self.t.translate_array(texts))
