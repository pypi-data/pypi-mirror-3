# -*- coding: utf-8 -*-

DATA_SET = [
    (
        [u"* first line",
         u""],

        [u"* first line\n",
         u"\n"]
    ),
    (
        [u"* first line"],

        [u"* first line\n"]
    ),
    (
        [u"* first line",
         u"  sub line"],

        [u"* first line sub line\n"]
    ),
    (
        [u"* first line",
         u"* second line",
         u""],

        [u"* first line\n",
         u"* second line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"* second line"],

        [u"* first line\n",
         u"* second line\n"]
    ),
    (
        [u"* first line",
         u"  * second line",
         u""],

        [u"* first line\n",
         u"  * second line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  * second line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  * second line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  * second line",
         u"    * third line",
         u""],

        [u"* first line\n",
         u"  * second line\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  sub line",
         u"  * second line",
         u"    * third line",
         u""],

        [u"* first line sub line\n",
         u"  * second line\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  * second line",
         u"    sub line",
         u"    * third line",
         u""],

        [u"* first line\n",
         u"  * second line sub line\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  * second line",
         u"    * third line",
         u"      sub line",
         u""],

        [u"* first line\n",
         u"  * second line\n",
         u"    * third line sub line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  sub line",
         u"  and then",
         u"  * second line",
         u"    * third line",
         u""],

        [u"* first line sub line and then\n",
         u"  * second line\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  * second line",
         u"    sub line",
         u"    and then",
         u"    * third line",
         u""],

        [u"* first line\n",
         u"  * second line sub line and then\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  * second line",
         u"    * third line",
         u"      sub line",
         u"      and then",
         u""],

        [u"* first line\n",
         u"  * second line\n",
         u"    * third line sub line and then\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  * second line",
         u"",
         u"    * third line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  * second line\n",
         u"\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  sub line",
         u"",
         u"  * second line",
         u"",
         u"    * third line",
         u""],

        [u"* first line sub line\n",
         u"\n",
         u"  * second line\n",
         u"\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  * second line",
         u"    sub line",
         u"",
         u"    * third line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  * second line sub line\n",
         u"\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  * second line",
         u"",
         u"    * third line",
         u"      sub line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  * second line\n",
         u"\n",
         u"    * third line sub line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"  sub line",
         u"  and then",
         u"",
         u"  * second line",
         u"",
         u"    * third line",
         u""],

        [u"* first line sub line and then\n",
         u"\n",
         u"  * second line\n",
         u"\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  * second line",
         u"    sub line",
         u"    and then",
         u"",
         u"    * third line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  * second line sub line and then\n",
         u"\n",
         u"    * third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  * second line",
         u"",
         u"    * third line",
         u"      sub line",
         u"      and then",
         u""],

        [u"* first line\n",
         u"\n",
         u"  * second line\n",
         u"\n",
         u"    * third line sub line and then\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  - second line",
         u"  - third line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  - second line\n",
         u"  - third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  - second line",
         u"",
         u"    - third line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  - second line\n",
         u"\n",
         u"    - third line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  - second line",
         u"",
         u"    * third line",
         u"",
         u"  - fourth line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  - second line\n",
         u"\n",
         u"    * third line\n",
         u"\n",
         u"  - fourth line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  - second line",
         u"",
         u"    * third line",
         u"      sub line",
         u"",
         u"  - fourth line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  - second line\n",
         u"\n",
         u"    * third line sub line\n",
         u"\n",
         u"  - fourth line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  - second line",
         u"",
         u"    * third line",
         u"      sub line",
         u"  - fourth line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  - second line\n",
         u"\n",
         u"    * third line sub line\n",
         u"  - fourth line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  - second line",
         u"",
         u"    * third line",
         u"    * fourth line",
         u"",
         u"  - fifth line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  - second line\n",
         u"\n",
         u"    * third line\n",
         u"    * fourth line\n",
         u"\n",
         u"  - fifth line\n",
         u"\n"]
    ),
    (
        [u"* first line",
         u"",
         u"  - second line",
         u"",
         u"    * third line",
         u"      sub line",
         u"    * fourth line",
         u"      sub line",
         u"",
         u"  - fifth line",
         u""],

        [u"* first line\n",
         u"\n",
         u"  - second line\n",
         u"\n",
         u"    * third line sub line\n",
         u"    * fourth line sub line\n",
         u"\n",
         u"  - fifth line\n",
         u"\n"]
    ),
]
