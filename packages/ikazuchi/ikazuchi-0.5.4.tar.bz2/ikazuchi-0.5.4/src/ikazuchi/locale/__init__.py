# -*- coding: utf-8 -*-

import gettext
from locale import *
from os.path import (dirname, realpath)

LOCALE_DIR = dirname(realpath(__file__))

t = gettext.translation("ikazuchi", localedir=LOCALE_DIR, fallback=True)
_ = t.ugettext
