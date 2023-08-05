# -*- coding: utf-8 -*-

import os
import re
from os.path import (dirname, realpath)

try:
    from ikazuchi.locale import _
except ImportError:
    def _(s): return s

def get_and_check_file_access(f, mode="r"):
    """ check access permission and return the file
    >>> import tempfile
    >>> f = tempfile.NamedTemporaryFile()
    >>> file_name = get_and_check_file_access(f.name)
    >>> f.name == file_name
    True
    >>> file_name = get_and_check_file_access(f.name, "w")
    >>> f.name == file_name
    True
    """
    if mode == "r":
        if not os.access(f, os.R_OK):
            raise  ValueError(_(u"Cannot access file: {0}").format(f))
    elif mode == "w":
        if not os.access(realpath(dirname(f)), os.W_OK):
            raise  ValueError(_(u"Cannot write file: {0}").format(f))
    return f

def concatenate_lines(lines, pattern):
    """ concatenate lines
    >>> import re
    >>> pattern = re.compile(r"(^\s+)(.+?)")
    >>> lines = [u"a", u" b", u" c", u" d", u"e"]
    >>> concatenate_lines(lines, pattern)
    [u'a', u' b c d', u'e']
    >>> lines = [u"a", u" b", u"  c", u"  d", u"e"]
    >>> concatenate_lines(lines, pattern)
    [u'a', u' b', u'  c d', u'e']
    >>> lines = [u"a", u" b", u"  c", u" d", u"e"]
    >>> concatenate_lines(lines, pattern)
    [u'a', u' b', u'  c', u' d', u'e']
    >>> lines = [u"a", u" b", u"c", u" d", u" e"]
    >>> concatenate_lines(lines, pattern)
    [u'a', u' b', u'c', u' d e']
    >>> lines = [u"a", u" b", u" c", u" d", u"  e"]
    >>> concatenate_lines(lines, pattern)
    [u'a', u' b c d', u'  e']
    >>> pattern = re.compile(r"(^\s*)(.+?)")
    >>> lines = [u"a", u"b", u"c", u" d", u"e"]
    >>> concatenate_lines(lines, pattern)
    [u'a b c', u' d', u'e']
    """
    _lines, prev_prefix = [], None
    for line in lines:
        match = re.search(pattern, line)
        if match:
            prefix, text = match.groups()
            if prev_prefix == prefix:
                _lines[-1] = u"{0} {1}".format(_lines[-1].rstrip(), text)
            else:
                _lines.append(line)
            prev_prefix = prefix
        else:
            _lines.append(line)
            prev_prefix = None
    return _lines

def get_multiline(lines, range_num):
    """ read lines every range_num
    >>> list(get_multiline(["a", "b", "c"], 2))
    [['a', 'b'], ['b', 'c']]
    >>> list(get_multiline(["a", "b", "c", "d"], 2))
    [['a', 'b'], ['b', 'c'], ['c', 'd']]
    >>> list(get_multiline(["a", "b", "c"], 3))
    [['a', 'b', 'c']]
    >>> list(get_multiline(["a", "b", "c", "d"], 3))
    [['a', 'b', 'c'], ['b', 'c', 'd']]
    >>> list(get_multiline(["a", "b"], 3))
    [['a', 'b']]
    >>> list(get_multiline(["a", "b"], 5))
    [['a', 'b']]
    >>> list(get_multiline([], 2))
    [[]]
    """
    to = range_num * (-1) + 1
    if len(lines) <= abs(to):
        yield lines
    else:
        for num, _ in enumerate(lines[:to]):
            yield lines[num:num + range_num]

def get_sequential_block(lines, compare_func):
    """
    >>> import re
    >>> pattern = re.compile(r"\w+")
    >>> cmp_func = lambda s: not re.search(pattern, s)
    >>> get_sequential_block([], cmp_func)
    (0, [])
    >>> get_sequential_block(["a", "b", "\\n"], cmp_func)
    (1, ['a', 'b'])
    >>> get_sequential_block(["a", "b", "c", "\\n"], cmp_func)
    (2, ['a', 'b', 'c'])
    >>> pattern = re.compile(r"\\n")
    >>> cmp_func = lambda s: re.search(pattern, s)
    >>> get_sequential_block(["a", "b", "c", "\\n"], cmp_func)
    (2, ['a', 'b', 'c'])
    """
    num = 0
    if len(lines) >= 2:
        for num, mline in enumerate(get_multiline(lines, 2)):
            if compare_func(mline[1]):
                break
        else:
            # maybe read out to EOF
            num += 1
    return num, lines[0:num + 1]

def get_east_asian_width(unicode_str):
    """
    Na: Narrow    1 半角英数
    H : Halfwidth 1 半角カナ
    W : Wide      2 全角文字
    F : Fullwidth 2 全角英数
    N : Neutral   1 アラビア文字
    A : Ambiguous 1 ギリシア文字、キリル文字(locale で幅が違う)
    >>> get_east_asian_width(unicode("1２3あいうabc", "utf-8"))
    13
    >>> get_east_asian_width(unicode("ﾊﾝｶｸｶﾅはどうかな？", "utf-8"))
    18
    >>> get_east_asian_width(unicode("スペース   全角　　　", "utf-8"))
    21
    >>> get_east_asian_width("string")
    6
    """
    from unicodedata import east_asian_width
    if type(unicode_str) is not unicode:
        unicode_str = unicode(unicode_str, "utf-8")
    width = 0
    for i in unicode_str:
        width += 1
        if east_asian_width(i) in ("W", "F"):
            width += 1
    return width

def zip_with_flatlist(list1, list2):
    """
    >>> zip_with_flatlist(range(3), range(3,6))
    [0, 3, 1, 4, 2, 5]
    >>> zip_with_flatlist(range(1), range(2,5))
    [0, 2]
    """
    _list = []
    for i, j in zip(list1, list2):
        _list.append(i)
        _list.append(j)
    return _list
