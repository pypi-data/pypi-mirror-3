# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile raimei' from vim"

from ikazuchi.core.translator import TRANSLATE_API
from ikazuchi.plugins.rstfile import reSTParser, reSTApiCaller
from ikazuchi.vim.utils import (to_encode, get_vim_variables,
                                get_apikey, get_translate_method)
from os.path import splitext

def get_target_lines(start, end, enc):
    _lines = vim.current.buffer[start:end]
    return [unicode("{0}\n".format(line), enc) for line in _lines]

def get_target_range():
    # take a range until next blank line if target range is not specified
    cur_row, cur_column = vim.current.window.cursor
    start = vim.current.range.start
    end = vim.current.range.end + 1
    if cur_row == end and (start + 1) == end:
        max_row = len(vim.current.buffer)
        while vim.current.buffer[end:end + 1] != [""] and end < max_row:
            end += 1
    return start, end

def translate_with_range(api_name, api_method, enc, lang_to):
    start, end = get_target_range()
    target_lines = get_target_lines(start, end, enc)
    caller = reSTApiCaller(reSTParser(target_lines).parse(), lang_to)
    trans = [l.encode(enc) for lines in caller.call(api_method) for l in lines]
    # previous and last empty lines are just for look and feel
    translated = ["", ] + trans + ["", ]
    # add translated text into vim
    vim.current.buffer.append(translated, end)
    vim.command("let raimei_target_lines={0}".format(
                to_encode(target_lines, enc)))
    print "Translated by {0}".format(api_name.title())

def translate(api_name, lang_from, lang_to, enc):
    translator = TRANSLATE_API[api_name](lang_from, lang_to, None)
    translator.set_apikey(get_apikey(api_name))
    api_method = get_translate_method(translator, api_name)
    translate_with_range(api_name, api_method, enc, lang_to)

def comment_out_original_lines():
    start, end = get_target_range()
    start += 1
    vim.current.buffer.append("..", start - 1)
    for num, line in enumerate(vim.current.buffer[start:end + 1]):
        vim.current.buffer[start + num] = "    {0}".format(line)

def main():
    try:
        vim_vars = get_vim_variables()
        translate(*vim_vars)
        ext = splitext(vim.current.buffer.name)[1][1:]
        if ext == "rst":
            comment_out_original_lines()
    except Exception as err:
        print "Got error: {0}".format(err)

if __name__ == "__main__":
    main()
