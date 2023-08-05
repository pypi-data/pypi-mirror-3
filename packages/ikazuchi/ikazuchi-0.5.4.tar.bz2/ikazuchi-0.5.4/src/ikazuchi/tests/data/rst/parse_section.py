# -*- coding: utf-8 -*-

DATA_SET = [
    (
        [u"=======\n",
         u"section\n",
         u"=======\n",
         u""],
        [("se",
          [u"=======\n",
           u"section\n",
           u"=======\n"],
          u""),
         2]
    ),
    (
        [u"=======\n",
         u"section\n",
         u"=======\n"],
        [("se",
          [u"=======\n",
           u"section\n",
           u"=======\n"],
          u""),
         2]
    ),
    (
        [u"=========\n",
         u" section\n",
         u"=========\n",
         u""],
        [("se",
          [u"=========\n",
           u" section\n",
           u"=========\n"],
          u""),
         2]
    ),
    (
        [u"=========\n",
         u" section \n",
         u"=========\n",
         u""],
        [("se",
          [u"=========\n",
           u" section \n",
           u"=========\n"],
          u""),
         2]
    ),
    (
        [u"previous sentence.\n",
         u"\n",
         u"*******\n",
         u"feature\n",
         u"*******\n",
         u""],
        [(None,
          [],
          u""),
         0]
    ),
    (
        [u"subsection\n",
         u"----------\n",
         u""],
        [("se",
          [u"subsection\n",
           u"----------\n",
           u""],
          u""),
         2]
    ),
    (
        [u"subsection\n",
         u"----------\n"],
        [("se",
          [u"subsection\n",
           u"----------\n"],
          u""),
         2]  # FIXME: consider later 1 or 2, which is correct?
    ),
]
