# -*- coding: utf-8 -*-

DATA_SET = [
    (   # no indent line
         u"no indent line.",

        [u"no indent line.\n"],
    ),
    (   # indent line
         u"  indent line.",

        [u"  indent line.\n"],
    ),
    (   # no indent and 1 sentece and others
         u"no indent line。next line",

        [u"no indent line。\n", u"next line\n"]
    ),
    (   # no indent and 2 senteces
         u"no indent line。next line。",

        [u"no indent line。\n", u"next line。\n"]
    ),
    (   # indent and 2 senteces
         u"  indent line。next line。",

        [u"  indent line。\n", u"  next line。\n"]
    ),
    (   # indent and 2 senteces, 2nd line has leading space
         u"  indent line。 next line。",

        [u"  indent line。\n", u"  next line。\n"]
    ),
    (   # complex lines
         u"  indent line。 next line。third line？ forth line！",

        [u"  indent line。\n",
         u"  next line。\n",
         u"  third line？\n",
         u"  forth line！\n"]
    ),
]
