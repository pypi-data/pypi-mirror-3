# -*- coding: utf-8 -*-

import argparse
import os
import sys

from core.handler import *
from locale import _

def get_lang():
    from locale import getdefaultlocale
    lang, country = getdefaultlocale()[0].split("_")
    return lang

def get_handler(opts):
    h = NullHandler()
    if opts.lang:
        h = LanguageHandler(opts.api, opts.encoding)
    elif opts.sentences:
        h = SingleSentenceHandler(opts)
    return h

class EncodingAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        enc = "".join(values.split()).split(",")
        enc_out = enc[1:] and enc[1] or enc[0]
        setattr(namespace, self.dest, [enc[0], enc_out])

def check_encoding(encoding):
    ret = []
    for enc in encoding:
        try:
            unicode("test", enc)
        except LookupError:
            ret.append(enc)
    return ret

def set_default_encoding(opts):
    from locale import getdefaultlocale
    enc = getdefaultlocale()[1]
    opts.encoding = [enc, enc]

def convert_str_to_unicode(opts):
    if opts.sentences:
        opts.sentences = [unicode(s, opts.encoding[0]) for s in opts.sentences]

def get_command(cmd, var="PATH"):
    import platform
    os_name = platform.system()
    delim = ";" if os_name == "Windows" else ":"
    # like a which command
    for path in os.getenv(var).split(delim):
        path_cmd = os.path.join(path, cmd)
        if os.access(path_cmd, os.X_OK):
            yield path_cmd

_UNSUPPORTED_VERSION = _("Unsupported Python version, use 2.6 above")

def check_python_version():
    if sys.version_info < (2, 6):
        print _UNSUPPORTED_VERSION
        sys.exit(0)
