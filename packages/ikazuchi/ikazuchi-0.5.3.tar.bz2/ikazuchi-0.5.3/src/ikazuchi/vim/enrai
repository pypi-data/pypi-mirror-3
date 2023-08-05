# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile enrai' from vim"

from ikazuchi.core.translator import TRANSLATE_API
from ikazuchi.vim.utils import (to_unicode, get_vim_variables,
                                get_apikey, get_translate_method)

def get_word_on_cursor(enc):
    words = to_unicode(vim.current.line.split(" "), enc)
    cur_row, cur_column = vim.current.window.cursor
    cur_column += 1  # add 1 since cursor column start from 0
    word_pos = 0
    for word in words:
        word_pos += len(word) + 1  # for whitespace
        if cur_column <= word_pos:
            return word
    return None

def translate_with_word(api_method, enc):
    word = get_word_on_cursor(enc)
    if word:
        api, trans = api_method([word])
        vim.command("let enrai_target_word='{0}'".format(word.encode(enc)))
        print "Translated by {0}: {1}".format(api, trans[0].encode(enc))

def translate(api_name, lang_from, lang_to, enc):
    t = TRANSLATE_API[api_name](lang_from, lang_to, None)
    t.set_apikey(get_apikey(api_name))
    api_method = get_translate_method(t, api_name)
    return translate_with_word(api_method, enc)

def main():
    try:
        vim_vars = get_vim_variables()
        translate(*vim_vars)
    except Exception as err:
        print "Got error: {0}".format(err)

if __name__ == "__main__":
    main()
