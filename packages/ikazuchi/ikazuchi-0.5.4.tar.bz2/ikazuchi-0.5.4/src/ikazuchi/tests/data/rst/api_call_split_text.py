# -*- coding: utf-8 -*-

DATA_SET = [
    (   # no indent line
         u"no indent line.",

        [u"no indent line."],
    ),
    (   # indent line
         u"  indent line.",

        [u"  indent line."],
    ),
    (   # no indent long line
         u"no indent long long long long long long long long long long "\
         u"long long long long long long long long long long long long "\
         u"long long long long line.",

        [u"no indent long long long long long long long long long long "\
         u"long long\nlong long long long long long long long long long "\
         u"long long long long\nline."]
    ),
    (   # indent long line
         u"  indent long long long long long long long long long long "\
         u"long long long long long long long long long long long long "\
         u"long long long long line.",

        [u"  indent long long long long long long long long long long "\
         u"long long\n  long long long long long long long long long long "\
         u"long long long\n  long line."]
    ),
]
