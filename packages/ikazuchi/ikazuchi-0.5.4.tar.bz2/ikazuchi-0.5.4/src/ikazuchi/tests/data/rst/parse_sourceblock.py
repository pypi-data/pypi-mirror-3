# -*- coding: utf-8 -*-

DATA_SET = [
    (
        [u"something::",
         u"",
         u"  first code",
         u"  second code",
         u""],
        [("so",
          [u"something::",
           u"",
           u"  first code",
           u"  second code",
           u""],
          u"something::"),
         4]
    ),
    (
        [u"something::",
         u"  first code",
         u"  second code",
         u""],
        [("so",
          [u"something::",
           u"  first code",
           u"  second code",
           u""],
          u"something::"),
         3]
    ),
    (
        [u"something::",
         u"",
         u"  first code",
         u"  second code"],
        [("so",
          [u"something::",
           u"",
           u"  first code",
           u"  second code"],
          u"something::"),
         3]
    ),
    (
        [u"something::",
         u"  first code",
         u"  second code"],
        [("so",
          [u"something::",
           u"  first code",
           u"  second code"],
          u"something::"),
         2]
    ),
    (
        [u"::",
         u"  first code"],
        [("so",
          [u"::",
           u"  first code"],
          u"::"),
         1]
    ),
    (
        [u"::  ",
         u"  first code"],
        [("so",
          [u"::  ",
           u"  first code"],
          u"::  "),
         1]
    ),
]
