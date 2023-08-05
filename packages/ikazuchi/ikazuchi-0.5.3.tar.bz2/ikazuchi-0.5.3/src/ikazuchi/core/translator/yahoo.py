# -*- coding: utf-8 -*-

import json
import urllib2
from contextlib import closing
from urllib import urlencode

__all__ = [
    "YahooTranslator",
]

class YahooTranslator(object):
    """
    Translator with Yahoo! Pipes
    http://pipes.yahoo.com/pipes/
    see also
    Yahoo! Pipes Terms of Use
    http://info.yahoo.com/legal/us/yahoo/pipes/pipes-4396.html
    """
    domain = "pipes.yahoo.com"
    common_path = "/t2y1979/"

    def __init__(self, lang_from, lang_to, handler):
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.handler = handler
        self._url = "http://{0}{1}".format(self.domain, self.common_path)
        self.query = {"_render": "json"}

    def _get_api(self, lang_from, lang_to):
        # convert for for arbitrary api name
        api = "{0}2{1}?".format(lang_from, lang_to)
        if lang_from == "ja" and lang_to == "en":
            api = "ja2en_?"
        elif lang_from == "en" and lang_to.lower() == "zh-cn":
            api = "en2zhcn?"
        elif lang_from == "en" and lang_to.lower() == "zh-tw":
            api = "en2zhtw?"
        return api

    def get_api_path(self, func):
        if func.func_name == "translate":
            return self._get_api(self.lang_from, self.lang_to)
        elif func.func_name == "detect":
            return "{0}?".format(func.func_name)

    def get_url(self, func, query):
        return "{0}{1}{2}".format(self._url,
                self.get_api_path(func), urlencode(query))

    def request(self, url):
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
        return res_json

    def call_api(self, func, query):
        """high-level method to make url and request"""
        url = self.get_url(func, query)
        response = self.request(url)
        return self.api(), response

    def detect(self, text):
        return self.api(), u"Not Supported"

    def translate(self, text):
        self.query.update(text=text.encode("utf-8"))
        api, response = self.call_api(self.translate, self.query)
        return api, response["value"]["items"][0]["description"]
