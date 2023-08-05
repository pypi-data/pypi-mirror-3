#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

from conf import (get_conf, get_conf_path)
from core.translator import TRANSLATE_API
from locale import _
from plugins.utils import (get_plugin, load_all_plugins)
from utils import *

__version__ = "0.5.3"

# base parser object for common option
base_parser = argparse.ArgumentParser(add_help=False)
base_parser.set_defaults(api=None, lang_from="en", lang_to=get_lang(),
                         encoding=None, quiet=False, verbose=False)
base_parser.add_argument("-a", "--api", dest="api", metavar="API",
                         help=u"APIs are {0}".format(TRANSLATE_API.keys()))
base_parser.add_argument("-e", "--encoding", dest="encoding",
                         action=EncodingAction, metavar="ENCODING",
                         help=u"input/output encoding")
base_parser.add_argument("-f", "--from", dest="lang_from", metavar="LANG",
                         help=u"original language")
base_parser.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                         help=u"not to show original sentence to stdout")
base_parser.add_argument("-t", "--to", dest="lang_to", metavar="LANG",
                         help=u"target language to translate")

# actual object by using ikazuchi command
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="plugin",
    help=u"available plugins. 'normal' means ikazuchi's standard feature "\
         u"so it can be abbreviated")

def get_args():
    normal_parser = subparsers.add_parser("normal", parents=[base_parser])
    normal_parser.set_defaults(detect=False, lang=False, sentences=[])
    normal_parser.add_argument("-d", "--detect", dest="detect",
        action="store_true", help=u"detect language for target sentence")
    normal_parser.add_argument("-l", "--languages", dest="lang",
        action="store_true", help=u"show supported languages")
    normal_parser.add_argument("-s", "--sentences", dest="sentences",
        nargs="+", metavar="SENTENCE", help=u"target sentences")
    normal_parser.add_argument("--version", action="version",
        version="%(prog)s {0}".format(__version__))

    # load subparsers from all plugins
    load_all_plugins()

    # little trick to abbreviate 'normal' keyword as default
    subparser_names = subparsers.choices.keys() + ["-h"]
    if not (len(sys.argv) >= 2 and sys.argv[1] in subparser_names):
        sys.argv[1:] = ["normal"] + sys.argv[1:]
    opts = parser.parse_args()

    if not opts.lang_to:
        opts.lang_to = raw_input(u"Type language code: ")

    err_msg = None
    if opts.encoding:
        err_encoding = check_encoding(opts.encoding)
        if err_encoding:
            err_msg = _(u"Unknown encodings: {0}").format(err_encoding)
    else:
        set_default_encoding(opts)

    # error check
    if not err_msg and opts.plugin == "normal":
        convert_str_to_unicode(opts)
        if not (opts.lang or opts.sentences):
            err_msg = _(u"Need to specify optional arguments")

    if err_msg:
        print err_msg
        sys.exit(0)

    return opts

def main():
    # pre process
    check_python_version()
    conf = get_conf(get_conf_path())
    # main process
    opts = get_args()
    if opts.plugin == "normal":
        handler = get_handler(opts)
    else:
        plugin_translator, handler = get_plugin(opts)
        if plugin_translator:
            TRANSLATE_API[opts.plugin] = plugin_translator
            opts.api = opts.api if opts.api else opts.plugin
    t = TRANSLATE_API[opts.api](opts.lang_from, opts.lang_to, handler)
    t.set_parameter_from_conf(conf)
    t.call_method_with_handler()

if __name__ == "__main__":
    main()
