# -*- coding: utf-8 -*-

from base import BaseHandler

class SingleSentenceHandler(BaseHandler):
    """
    Handler class for translating single sentence
    """
    def __init__(self, opts):
        self.sentences = opts.sentences
        self.encoding = opts.encoding
        self.quiet = opts.quiet
        if opts.api == "microsoft":
            self.method_name = "translate_array"
        if opts.detect:
            self.method_name = "detect"
            if opts.api == "microsoft":
                self.method_name = "detect_array"

    def _encode(self, text):
        return text.encode(self.encoding[1])

    def _call_method(self, api_method):
        api, result = api_method(self.sentences)
        _method = self.method_name.replace("_array", "")  # for microsoft
        _method = u"{0}({1}):".format(_method, api)
        for num, s in enumerate(self.sentences):
            if not self.quiet:
                print self._encode(u"{0:25}{1}".format("sentence:", s))
            print self._encode(u"{0:25}{1}".format(_method, result[num]))
