# -*- coding: utf-8 -*-

DATA_SET = [
    (
        [u".. note::",
         u"",
         u"  first line",
         u"  second line",
         u""],
        [("d",
          [u".. note::",
           u"",
           u"  first line",
           u"  second line",
           u""],
          u".. note::"),
         4]
    ),
    (
        [u".. note::",
         u"  first line",
         u"  second line",
         u""],
        [("d",
          [u".. note::",
           u"  first line",
           u"  second line",
           u""],
          u".. note::"),
         3]
    ),
    (
        [u".. note::",
         u"  first line",
         u"  second line"],
        [("d",
          [u".. note::",
           u"  first line",
           u"  second line"],
          u".. note::"),
         2]
    ),
    (
        [u".. note::   ",
         u"  first line"],
        [("d",
          [u".. note::   ",
           u"  first line"],
          u".. note::   "),
         1]
    ),
    (
        [u".. image:: first.png",
         u".. image:: second.png",
         u""],
        [("d",
          [u".. image:: first.png"],
          u".. image:: first.png"),
         0]
    ),
    (
        [u".. image:: first.png",
         u"",
         u".. image:: second.png",
         u""],
        [("d",
          [u".. image:: first.png",
           u""],
          u".. image:: first.png"),
         1]
    ),
]
