# -*- coding: utf-8 -*-

DATA_SET = [
    (
        [u"| first line",
         u"| second line",
         u""],
        [("ln",
          [u"| first line",
           u"| second line"],
          u""),
         1]
    ),
    (
        [u"| first line",
         u"| second line"],
        [("ln",
          [u"| first line",
           u"| second line"],
          u""),
         1]
    ),
    (
        [u"| first line",
         u"|   second line",
         u""],
        [("ln",
          [u"| first line",
           u"|   second line"],
          u""),
         1]
    ),
    (
        [u"| first line",
         u"|   second line",
         u"|     third line",
         u""],
        [("ln",
          [u"| first line",
           u"|   second line",
           u"|     third line"],
          u""),
         2]
    ),
    (
        [u"| first line",
         u"|   second line",
         u"|     third line",
         u"|   fourth line",
         u""],
        [("ln",
          [u"| first line",
           u"|   second line",
           u"|     third line",
           u"|   fourth line"],
          u""),
         3]
    ),
    (
        [u"| first line",
         u"|",
         u"|   second line",
         u""],
        [("ln",
          [u"| first line",
           u"|",
           u"|   second line"],
          u""),
         2]
    ),
    (
        [u"| first line",
         u"|",
         u"|   second line",
         u"|",
         u""],
        [("ln",
          [u"| first line",
           u"|",
           u"|   second line",
           u"|"],
          u""),
         3]
    ),
]
