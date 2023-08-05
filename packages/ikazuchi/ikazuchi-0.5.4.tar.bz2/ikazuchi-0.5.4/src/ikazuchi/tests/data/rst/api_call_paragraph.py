# -*- coding: utf-8 -*-

DATA_SET = [
    # normal paragraph
    (
        [u"*first line*"],

        [u"<span class=notranslate>*first line*</span>"]
    ),
    (
        [u"first line",
         u"**second line**"],

        [u"first line <span class=notranslate>**second line**</span>"]
    ),
    (
        [u"first line",
         u"second line",
         u"``third line``"],

        [u"first line second line "\
         u"<span class=notranslate>``third line``</span>"]
    ),
    (
        [u"first line",
         u"  **second line**"],

        [u"first line",
         u"  <span class=notranslate>**second line**</span>"]
    ),
    (
        [u"first line",
         u"  second line",
         u"    ``third line``"],

        [u"first line",
         u"  second line",
         u"    <span class=notranslate>``third line``</span>"]
    ),
    (
        [u"first line",
         u"  second line",
         u"    third line",
         u"  fourth line"],

        [u"first line",
         u"  second line",
         u"    third line",
         u"  fourth line"],
    ),
    (   # auto line break with textwrap
        [u"long long long long long long long long long long first line",
         u"looooooooooooooooooooooooooooooooooooooooong **second line**"],

        [u"long long long long long long long long long long first line\n"\
          "looooooooooooooooooooooooooooooooooooooooong <span\n"\
          "class=notranslate>**second line**</span>"]
    ),
    (   # role
        [u":mod:`ikazuchi` has some functions, ",
         u":func:`translate` and :func:`detect`."],

        [u"<span class=notranslate>:mod:`ikazuchi`</span> has some "\
         u"functions,\n<span class=notranslate>:func:`translate`</span> "\
         u"and <span\nclass=notranslate>:func:`detect`</span>."]
    ),

    # paragraph with indent
    (
        [u"  *first line*"],

        [u"  <span class=notranslate>*first line*</span>"]
    ),
    (
        [u"  first line",
         u"  **second line**"],

        [u"  first line <span class=notranslate>**second line**</span>"]
    ),
    (
        [u"  first line",
         u"  second line",
         u"  ``third line``"],

        [u"  first line second line "\
         u"<span class=notranslate>``third line``</span>"]
    ),
    (
        [u"  first line",
         u"    **second line**"],

        [u"  first line",
         u"    <span class=notranslate>**second line**</span>"]
    ),
    (
        [u"  first line",
         u"    second line",
         u"      ``third line``"],

        [u"  first line",
         u"    second line",
         u"      <span class=notranslate>``third line``</span>"]
    ),
    (
        [u"  first line",
         u"    second line",
         u"      third line",
         u"    fourth line"],

        [u"  first line",
         u"    second line",
         u"      third line",
         u"    fourth line"],
    ),
    (   # auto line break with textwrap
        [u"  long long long long long long long long long long first line",
         u"  looooooooooooooooooooooooooooooooooooooooong **second line**"],

        [u"  long long long long long long long long long long first line\n"\
          "  looooooooooooooooooooooooooooooooooooooooong <span\n"\
          "  class=notranslate>**second line**</span>"]
    ),
    (   # role
        [u"  :mod:`ikazuchi` has some functions, ",
         u"  :func:`translate` and :func:`detect`."],

        [u"  <span class=notranslate>:mod:`ikazuchi`</span> has some "\
         u"functions,\n  <span class=notranslate>:func:`translate`</span> "\
         u"and <span\n  class=notranslate>:func:`detect`</span>."]
    ),
]
