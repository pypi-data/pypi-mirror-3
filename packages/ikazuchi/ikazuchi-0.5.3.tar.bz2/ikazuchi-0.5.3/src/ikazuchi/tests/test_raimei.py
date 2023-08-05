# -*- coding: utf-8 -*-

from minimock import mock, Mock, restore
from nose.tools import *

# functions for test
from ikazuchi.vim import (raimei, utils)

class TestRaimei(object):

    eval_var = {
        "raimei_api": "google",
        "raimei_from": "en",
        "raimei_to": "ja",
        "&enc": "utf-8",
    }

    def setup(self):
        raimei.vim = None
        mock("raimei.vim")
        raimei.vim.current = Mock("current",
            window=Mock("window",
                cursor=Mock("cursor"),
            ),
            range=Mock("range",
                start=Mock("start"),
                end=Mock("end"),
            ),
        )
        utils.vim = None
        mock("utils.vim")
        _eval_func = lambda var: self.eval_var[var]
        utils.vim.eval = Mock("eval", returns_func=_eval_func)

    def teardown(self):
        restore()

    def test_get_vim_variables(self):
        ret = (
            self.eval_var["raimei_api"],
            self.eval_var["raimei_from"],
            self.eval_var["raimei_to"],
            self.eval_var["&enc"],
        )
        assert_equal(ret, raimei.get_vim_variables())

    def test_get_target_range(self):
        class Buffer(Mock):
            buf = ["first line", "second line", "third line",
                   "fourth line", "fifth line", ""]

            def __len__(self):
                return len(self.buf)

            def __getitem__(self, i):
                return self.buf[i]

        raimei.vim.current.buffer = Buffer("buffer")
        raimei.vim.current.range.start = 2
        raimei.vim.current.range.end = 2
        raimei.vim.current.window.cursor = (3, 0)
        assert_equal((2, 5), raimei.get_target_range())
        # other line on the cursor, only single line range is specified
        raimei.vim.current.window.cursor = (1, 0)
        assert_equal((2, 3), raimei.get_target_range())

    def test_get_target_range_infinite(self):
        class Buffer(Mock):
            buf = ["first line", "second line", "third line"]

            def __len__(self):
                return len(self.buf)

            def __getitem__(self, i):
                return self.buf[i]

        raimei.vim.current.buffer = Buffer("buffer")
        # from 1st line
        raimei.vim.current.range.start = 0
        raimei.vim.current.range.end = 0
        raimei.vim.current.window.cursor = (1, 0)
        assert_equal((0, 3), raimei.get_target_range())
        # from 2nd line
        raimei.vim.current.range.start = 1
        raimei.vim.current.range.end = 1
        raimei.vim.current.window.cursor = (2, 0)
        assert_equal((1, 3), raimei.get_target_range())
