# -*- coding: utf-8 -*-

DATA_SET = [
    # normal paragraph
    (
        [u"first line",
         u"second line",
         u""],
        [("p",
          [u"first line",
           u"second line"],
          u""),
         1]
    ),
    (
        [u"first line",
         u"second line"],
        [("p",
          [u"first line",
           u"second line"],
          u""),
         1]
    ),
    (
        [u"first line"],
        [("p",
          [u"first line"],
          u""),
         0]
    ),
    (
        [u"first line",
         u"  second line"],
        [("p",
          [u"first line",
           u"  second line"],
          u""),
         1]
    ),
    (
        [u"first line",
         u"  second line",
         u"    third line"],
        [("p",
          [u"first line",
           u"  second line",
           u"    third line"],
          u""),
         2]
    ),
    (
        [u"first line",
         u"  second line",
         u"    third line",
         u"  fourth line"],
        [("p",
          [u"first line",
           u"  second line",
           u"    third line",
           u"  fourth line"],
          u""),
         3]
    ),

    # paragraph with indent
    (
        [u"  first line",
         u"  second line",
         u""],
        [("p",
          [u"  first line",
           u"  second line"],
          u""),
         1]
    ),
    (
        [u"  first line",
         u"  second line"],
        [("p",
          [u"  first line",
           u"  second line"],
          u""),
         1]
    ),
    (
        [u"  first line"],
        [("p",
          [u"  first line"],
          u""),
         0]
    ),
    (
        [u"  first line",
         u"    second line"],
        [("p",
          [u"  first line",
           u"    second line"],
          u""),
         1]
    ),
    (
        [u"  first line",
         u"    second line",
         u"      third line"],
        [("p",
          [u"  first line",
           u"    second line",
           u"      third line"],
          u""),
         2]
    ),
    (
        [u"  first line",
         u"    second line",
         u"      third line",
         u"    fourth line"],
        [("p",
          [u"  first line",
           u"    second line",
           u"      third line",
           u"    fourth line"],
          u""),
         3]
    ),
]
