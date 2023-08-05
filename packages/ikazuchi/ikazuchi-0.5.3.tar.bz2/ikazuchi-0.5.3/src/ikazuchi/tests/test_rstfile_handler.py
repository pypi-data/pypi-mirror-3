# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.plugins.rstfile import *

class TestreSTParser(object):

    def _test_func(self, data_set, func):
        # common assert function for each test
        _class = self.__class__.__name__
        _func = func.func_name
        _fmt = u"{0}.{1}_{2} ({3} ...)"
        for num, (data, expected) in enumerate(data_set):
            name = _fmt.format(_class, _func, num, str(data)[:10])
            _assert = lambda e, a: assert_equal(e, a)
            _assert.description = name
            yield _assert, expected, list(func(data))

    def test_get_directive(self):
        from data.rst.parse_directive import DATA_SET
        for r in self._test_func(DATA_SET, reSTParser.get_directive):
            yield r

    def test_get_sourceblock(self):
        from data.rst.parse_sourceblock import DATA_SET
        for r in self._test_func(DATA_SET, reSTParser.get_sourceblock):
            yield r

    def test_get_lineblock(self):
        from data.rst.parse_lineblock import DATA_SET
        for r in self._test_func(DATA_SET, reSTParser.get_lineblock):
            yield r

    def test_get_listblock(self):
        from data.rst.parse_listblock import DATA_SET
        for r in self._test_func(DATA_SET, reSTParser.get_listblock):
            yield r

    def test_get_tableblock(self):
        from data.rst.parse_tableblock import DATA_SET
        for r in self._test_func(DATA_SET, reSTParser.get_tableblock):
            yield r

    def test_get_section(self):
        from data.rst.parse_section import DATA_SET
        for r in self._test_func(DATA_SET, reSTParser.get_section):
            yield r

    def test_get_paragraph(self):
        from data.rst.parse_paragraph import DATA_SET
        for r in self._test_func(DATA_SET, reSTParser.get_paragraph):
            yield r


class TestreSTApiCaller(object):

    def __init__(self):
        self.caller = reSTApiCaller(None, "en")
        self._class = self.__class__.__name__
        self._fmt = u"{0}.{1}_{2}"

    def _test_func(self, data_set, func):
        # common assert function for each test
        _func = func.func_name
        for num, (data, expected) in enumerate(data_set):
            name = self._fmt.format(self._class, _func, num)
            _assert = lambda e, a: assert_equal(e, a)
            _assert.description = name
            yield _assert, expected, func(data)

    def _call_func(self, data_set, func):
        # common assert function for each test calling api method
        def dummy(text):
            # return given text as is
            return None, text

        _func = func.func_name
        for num, data in enumerate(data_set):
            args, expected = data[:-1], data[-1]
            name = self._fmt.format(self._class, _func, num, str(data)[:10])
            _, actual = func(dummy, *args)
            _assert = lambda e, a: assert_equal(e, a)
            _assert.description = name
            yield _assert, expected, actual

    def test_get_table_column_width(self):
        from data.rst.api_call_get_table_column_width import DATA_SET
        _func = u"test_get_table_column_width"
        for num, (items, width, expected) in enumerate(DATA_SET):
            actual = reSTApiCaller.get_table_column_width(items, width)
            name = self._fmt.format(self._class, _func, num, str(items)[:10])
            _assert = lambda e, a: assert_equal(e, a)
            _assert.description = name
            yield _assert, expected, actual

    def test_get_indent_and_text(self):
        from data.rst.api_call_text_with_indent import DATA_SET
        for r in self._test_func(DATA_SET, reSTApiCaller.get_indent_and_text):
            yield r

    def test_markup_paragraph_notranslate(self):
        from data.rst.api_call_markup_notranslate import DATA_SET
        for r in self._test_func(DATA_SET,
                    reSTApiCaller.markup_paragraph_notranslate):
            yield r

    def test_split_text_into_multiline(self):
        self.caller.lang_to = "en"
        from data.rst.api_call_split_text import DATA_SET
        _func = self.caller.split_text_into_multiline
        for r in self._test_func(DATA_SET, _func):
            yield r

    def test_split_text_into_multiline_ja(self):
        self.caller.lang_to = "ja"
        from data.rst.api_call_split_text_ja import DATA_SET
        _func = self.caller.split_text_into_multiline
        for r in self._test_func(DATA_SET, _func):
            yield r

    def test_call_for_directive(self):
        from data.rst.api_call_directive import DATA_SET
        for r in self._call_func(DATA_SET, self.caller._call_for_directive):
            yield r

    def test_call_for_sourceblock(self):
        from data.rst.api_call_sourceblock import DATA_SET
        for r in self._call_func(DATA_SET, self.caller._call_for_sourceblock):
            yield r

    def test_call_for_lineblock(self):
        from data.rst.api_call_lineblock import DATA_SET
        for r in self._call_func(DATA_SET, self.caller._call_for_lineblock):
            yield r

    def test_call_for_listblock(self):
        from data.rst.api_call_listblock import DATA_SET
        for r in self._call_func(DATA_SET, self.caller._call_for_listblock):
            yield r

    def test_call_for_tableblock(self):
        from data.rst.api_call_tableblock import DATA_SET
        for r in self._call_func(DATA_SET, self.caller._call_for_tableblock):
            yield r

    def test_call_for_section(self):
        from data.rst.api_call_section import DATA_SET
        for r in self._call_func(DATA_SET, self.caller._call_for_section):
            yield r

    def test_call_for_paragraph(self):
        from data.rst.api_call_paragraph import DATA_SET
        for r in self._call_func(DATA_SET, self.caller._call_for_paragraph):
            yield r
