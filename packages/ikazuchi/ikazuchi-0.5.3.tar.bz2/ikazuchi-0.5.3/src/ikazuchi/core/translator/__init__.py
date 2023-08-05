# -*- coding: utf-8 -*-

import abc
import re
import utils
from collections import defaultdict

from google import GoogleTranslator
from microsoft import MicrosoftTranslator
from yahoo import YahooTranslator
from ikazuchi.conf import show_how_to_get_apikey

__all__ = [
    "TRANSLATE_API",
]

class BaseTranslator(object):
    """Base class for Translator"""

    __metaclass__ = abc.ABCMeta
    api = lambda klass: klass.__class__.__name__.replace("Translating", "")
    # FIXME: span tag only, cannot match for minimal when html tag is nested
    notrans_tag = re.compile(
        r"<span class=[\"']?notranslate[\"']?>(.*?)</span>", re.IGNORECASE)
    whitespaces = re.compile(r"\s+", re.UNICODE)
    zerowidth = re.compile(u"\u200b|\u200c|\u200d|\ufeff", re.UNICODE)
    colon = re.compile(u"\s+(:+)$", re.UNICODE)

    @abc.abstractmethod
    def __init__(self, lang_from, lang_to, handler):
        """Overridden by MixIn class
        must be set "self.handler = handler"
        """

    @abc.abstractmethod
    def translate(self, text): pass

    def call_method_with_handler(self):
        method = getattr(self, self.handler.method_name)
        self.handler._call_method(method)

    def parse_html(self, html):
        from StringIO import StringIO
        from formatter import (AbstractFormatter, DumbWriter)
        from htmllib import HTMLParser
        _html = re.sub(self.notrans_tag, r" \1 ", html)
        buf = StringIO()
        p = HTMLParser(AbstractFormatter(DumbWriter(buf)))
        p.feed(_html)
        _sub = re.sub(self.whitespaces, " ", buf.getvalue())
        # FIXME: how can zerowidth be removed more simply?
        _sub = re.sub(self.zerowidth, "", _sub)
        _sub = re.sub(self.colon, r"\1", _sub)
        return _sub

    def set_apikey(self, key):
        self.apikey = key

    def set_apikey_from_conf(self, conf):
        _key = conf.get(self.api().lower(), "apikey")
        if _key:
            self.apikey = _key
        else:
            show_how_to_get_apikey()

    def set_parameter_from_conf(self, conf):
        import os
        from functools import partial
        general = partial(conf.get, "general")
        # urllib2.build_opener() skips ProxyHandler for Python 2.6/2.7
        # see also: http://bugs.python.org/issue7152#msg94150
        # so, the proxy settings set environment variable as workaround
        if general("http_proxy"):
            os.environ["http_proxy"] = general("http_proxy")
        if general("https_proxy"):
            os.environ["https_proxy"] = general("https_proxy")
        self.set_apikey_from_conf(conf)

# MixIn each implemented Translator
class TranslatingGoogle(GoogleTranslator, BaseTranslator): pass
class TranslatingMicrosoft(MicrosoftTranslator, BaseTranslator): pass
class TranslatingYahoo(YahooTranslator, BaseTranslator): pass  # is obsoleted

TRANSLATE_API = defaultdict(lambda: TranslatingGoogle,
    {
        "google": TranslatingGoogle,
        "microsoft": TranslatingMicrosoft,
    }
)
