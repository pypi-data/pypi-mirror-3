# -*- coding: utf-8 -*-

import json
import urllib2
from contextlib import closing
from urllib import urlencode
from utils import get_ip_address

from ikazuchi.errors import NeedApiKeyError

__all__ = [
    "GoogleTranslator",
]

class GoogleTranslator(object):
    """
    Translator with Google Translate API with version 2
    http://code.google.com/intl/ja/apis/language/translate/overview.html
    http://code.google.com/intl/ja/apis/language/translate/v2/using_rest.html
    http://code.google.com/intl/ja/apis/language/translate/v2/pricing.html
    see also
    Google Translate API Terms of Use
    http://code.google.com/intl/ja/apis/language/translate/terms.html
    """
    domain = "www.googleapis.com"
    common_path = "/language/translate/"
    apikey = None  # get from configuration file
    q_format = "html"

    def __init__(self, lang_from, lang_to, handler):
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.handler = handler
        self._url = "https://{0}{1}".format(self.domain, self.common_path)

    def get_url(self, func=None):
        if func:
            url = "{0}v2/{1}".format(self._url, func.func_name)
        else:
            url = "{0}v2".format(self._url)
        return url

    def request(self, url, data):
        req = urllib2.Request(url)
        req.add_header("X-HTTP-Method-Override", "GET")
        req.add_data(data)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
        return res_json["data"]

    def call_api(self, query, key, func=None):
        """high-level method to make url and request"""
        if not self.apikey:
            raise NeedApiKeyError("need API key !!!")
        url = self.get_url(func)
        response = self.request(url, urlencode(query, doseq=True))
        return self.api(), response[key]

    def detect(self, texts):
        """ Detect Language
        http://code.google.com/intl/ja/apis/language/translate/v2/\
        using_rest.html#detect-language
        """
        query = {
            "key": self.apikey,
            "q": [t.encode("utf-8") for t in texts],
        }
        return self.call_api(query, u"detections", func=self.detect)

    def languages(self):
        """ Discover Supported Languages
        http://code.google.com/intl/ja/apis/language/translate/v2/\
        using_rest.html#supported-languages
        """
        query = {
            "key": self.apikey,
            "target": self.lang_to,
        }
        return self.call_api(query, u"languages", func=self.languages)

    def translate(self, texts):
        """ Translate Text
        http://code.google.com/intl/ja/apis/language/translate/v2/\
        using_rest.html#Translate
        """
        query = {
            "format": self.q_format,
            "key": self.apikey,
            "q": [t.encode("utf-8") for t in texts],
            "source": self.lang_from,
            "target": self.lang_to,
        }
        api, response = self.call_api(query, u"translations")
        return api, [self.parse_html(r[u"translatedText"]) for r in response]

    def translate_tts(self, text, lang, f):
        """ Unofficial Google Text To Speech API
        http://weston.ruter.net/projects/google-tts/
        """
        headers = {"User-Agent":
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-US) "
            "AppleWebKit/534.16 (KHTML, like Gecko) "
            "Chrome/10.0.648.204 Safari/534.16"
        }
        query = {"tl": lang, "q": text.encode("utf-8")}
        url = "http://translate.google.com/translate_tts?{0}".format(
                urlencode(query))
        req = urllib2.Request(url, None, headers)
        with closing(urllib2.urlopen(req)) as res:
            f.write(res.read())
            f.flush()
        return self.api()
