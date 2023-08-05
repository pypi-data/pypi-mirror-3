# -*- coding: utf-8 -*-

import abc

class BaseHandler(object):
    """Base class for handler"""

    __metaclass__ = abc.ABCMeta

    method_name = "translate"

    @abc.abstractmethod
    def _call_method(self, method): pass

class NullHandler(BaseHandler):
    """Handler class for Null object"""
    def _call_method(self, method):
        pass  # having nothing to do

class LanguageHandler(BaseHandler):
    """Handler class for languages API"""
    def __init__(self, api, encoding):
        self.api = api
        self.encoding = encoding
        if self.api == "google":
            self.method_name = "languages"
        elif self.api == "microsoft":
            self.method_name = "get_languages_for_translate"
        else:
            raise NotImplementedError("Not Supported")

    def _encode(self, text):
        return text.encode(self.encoding[1])

    def _call_method(self, api_method):
        api, result = api_method()
        for r in result:
            _method = u"{0}({1}):".format(self.method_name, api)
            if self.api == "google":
                print self._encode(u"{0:25}{language:5} {name}".format(
                                   _method, **r))
            else:
                print self._encode(u"{0:25} {1}".format(_method, r))
