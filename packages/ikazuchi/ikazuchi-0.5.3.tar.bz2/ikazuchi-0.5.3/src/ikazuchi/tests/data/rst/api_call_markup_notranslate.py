# -*- coding: utf-8 -*-

DATA_SET = [
    (   # inline markup 1
        u"rest *inline* **markup** is very ``simple``.",

        u"rest <span class=notranslate>*inline*</span> "\
        u"<span class=notranslate>**markup**</span> is very "\
        u"<span class=notranslate>``simple``</span>."
    ),
    (   # inline markup 2
        u"Now, `ikazuchi` is under development.",

        u"Now, <span class=notranslate>`ikazuchi`</span> "\
        u"is under development."
    ),
    (   # inline markup 3
        u"The relation ``Translator`` and ``Handler``.",

        u"The relation <span class=notranslate>``Translator``</span> and "\
        u"<span class=notranslate>``Handler``</span>."
    ),
    (   # hyper link 1
        u"a link `ikazuchi <http://pypi.python.org/pypi/ikazuchi/>`_",

        u"a link <span class=notranslate>`ikazuchi &lt;"\
        u"http://pypi.python.org/pypi/ikazuchi/&gt;`_</span>",
    ),
    (   # hyper link 2
        u".. _ikazuchi: http://pypi.python.org/pypi/ikazuchi/",

        u"<span class=notranslate>.. _ikazuchi: "\
        u"http://pypi.python.org/pypi/ikazuchi/</span>"
    ),
    (   # hyper link 3
        u"unwrapped link http://pypi.python.org/pypi/ikazuchi/",

        u"unwrapped link <span class=notranslate>"\
        u"http://pypi.python.org/pypi/ikazuchi/</span>"
    ),
    (   # hyper link 4
        u"a link name `ikazuchi`__",

        u"a link name <span class=notranslate>`ikazuchi`__</span>"
    ),
    (   # hyper link 5
        u"__ http://pypi.python.org/pypi/ikazuchi/",

        u"<span class=notranslate>__ "\
        u"http://pypi.python.org/pypi/ikazuchi/</span>"
    ),
    (   # text containing '&'
        u"$ chrome &",

        u"$ chrome &amp;"
    ),
    (   # role
        u"it can :role:`name`, for example :mod:`ikazuchi`.",

        u"it can <span class=notranslate>:role:`name`</span>, "\
        u"for example <span class=notranslate>:mod:`ikazuchi`</span>."
    ),
    (   # rubric 1
        u"ikazuchi [#f1]_ is a tool.",

        u"ikazuchi <span class=notranslate>[#f1]_</span> is a tool."
    ),
    (   # rubric 2
        u".. [#f1] ikazuchi's document",

        u"<span class=notranslate>.. [#f1] ikazuchi's document</span>"
    ),
    (   # reference 1
        u"ikazuchi [ref]_ is a tool.",

        u"ikazuchi <span class=notranslate>[ref]_</span> is a tool."
    ),
    (   # reference 2
        u".. [ref] ikazuchi's document",

        u"<span class=notranslate>.. [ref] ikazuchi's document</span>"
    ),
    (   # source 1
        u"description: that is, ",

        u"description<span class=notranslate>: </span>that is, "
    ),
    (   # source 2
        u"::\n  source\n  block",

        u"<span class=notranslate>::\n  </span>source\n  block"
    ),
]
