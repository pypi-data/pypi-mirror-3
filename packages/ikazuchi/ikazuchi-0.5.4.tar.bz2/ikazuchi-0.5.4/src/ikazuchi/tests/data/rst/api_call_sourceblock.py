# -*- coding: utf-8 -*-

DATA_SET = [
    # standalone sourceblock
    (
        [u"::\n"
         u"",
         u"    first code",
         u"    second code",
         u""],
        u"::\n",

        [u"::\n",
         u"    first code",
         u"    second code",
         u""]
    ),
    (
        [u"::\n"
         u"",
         u"    first code",
         u"    second code"],
        u"::\n",

        [u"::\n",
         u"    first code",
         u"    second code"]
    ),
    (
        [u"::\n"
         u"",
         u"",
         u"    first code",
         u"    second code"],
        u"::\n",

        [u"::\n"
         u"",
         u"",
         u"    first code",
         u"    second code"]
    ),
    (
        [u"::  \n"
         u"",
         u"    first code",
         u"    second code",
         u""],
        u"::  \n",

        [u"::  \n",
         u"    first code",
         u"    second code",
         u""]
    ),
    (
        [u"::\n"
         u"    first code",
         u"    second code",
         u""],
        u"::\n",

        [u"::\n    first code",
         u"    second code",
         u""]
    ),

    # given first line has "::" and test
    (
        [u"that is::\n"
         u"",
         u"    first code",
         u"    second code",
         u""],
        u"that is::\n",

        [u"that is<span class=notranslate>::</span>",
         u"    first code",
         u"    second code",
         u""]
    ),
    (
        [u"that is::\n"
         u"",
         u"    first code",
         u"    second code"],
        u"that is::\n",

        [u"that is<span class=notranslate>::</span>",
         u"    first code",
         u"    second code"]
    ),
    (
        [u"that is::\n"
         u"",
         u"",
         u"    first code",
         u"    second code"],
        u"that is::\n",

        [u"that is<span class=notranslate>::</span>",
         u"",
         u"    first code",
         u"    second code"]
    ),
    (
        [u"that is::  \n"
         u"",
         u"    first code",
         u"    second code",
         u""],
        u"that is::  \n",

        [u"that is<span class=notranslate>::  </span>",
         u"    first code",
         u"    second code",
         u""]
    ),
    (
        [u"that is::\n",
         u"    first code",
         u"    second code",
         u""],
        u"that is::\n",

        [u"that is<span class=notranslate>::</span>",
         u"    first code",
         u"    second code",
         u""]
    ),
]
