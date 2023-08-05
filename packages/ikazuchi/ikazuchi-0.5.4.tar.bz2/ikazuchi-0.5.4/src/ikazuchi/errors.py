# -*- coding: utf-8 -*-

class IkazuchiError(Exception):
    """ ikazuchi root exception """
    pass

class TranslatorError(IkazuchiError):
    """ ikazuchi translator exception """
    pass

class NeedApiKeyError(TranslatorError): pass
