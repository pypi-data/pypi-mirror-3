# -*- coding: utf-8 -*-

DATA_SET = [
    (
        u"text line",
        (u"", u"text line")
    ),
    (
        u"  ",
        (u" ", u" ")
    ),
    (
        u" \t ",
        (u" \t", u" ")
    ),
    (
        u"  text line",
        (u"  ", u"text line")
    ),
    (
        u"\ttext line",
        (u"\t", u"text line")
    ),
    (
        u"\t  text line",
        (u"\t  ", u"text line")
    ),
    (
        u"\t  \ntext line",
        (u"\t  \n", u"text line")
    ),
]
