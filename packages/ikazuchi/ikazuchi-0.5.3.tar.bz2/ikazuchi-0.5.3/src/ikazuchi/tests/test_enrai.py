# -*- coding: utf-8 -*-

from minimock import mock, Mock, restore
from nose.tools import *

# functions for test
from ikazuchi.vim import enrai

class TestEnrai(object):

    eval_var = {
        "raimei_api": "google",
        "raimei_from": "en",
        "raimei_to": "ja",
        "&enc": "utf-8",
    }

    test_text = " \t   Enrai is translated   as 'Distant thunder'."

    def setup(self):
        enrai.vim = None
        mock("enrai.vim")
        _eval_func = lambda var: self.eval_var[var]
        enrai.vim.eval = Mock("eval", returns_func=_eval_func)
        enrai.vim.current = Mock("current",
            window=Mock("window"),
            line=Mock("line",
                split=Mock("split", returns=self.test_text.split(" ")),
            ),
        )

    def teardown(self):
        restore()

    def test_get_word_on_cursor_1(self):
        _enc = self.eval_var["&enc"]
        enrai.vim.current.window.cursor = (1, 6)
        assert_equal("Enrai", enrai.get_word_on_cursor(_enc))

    def test_get_word_on_cursor_2(self):
        _enc = self.eval_var["&enc"]
        enrai.vim.current.window.cursor = (1, 12)
        assert_equal("is", enrai.get_word_on_cursor(_enc))

    def test_get_word_on_cursor_3(self):
        _enc = self.eval_var["&enc"]
        enrai.vim.current.window.cursor = (1, 32)
        assert_equal("'Distant", enrai.get_word_on_cursor(_enc))
