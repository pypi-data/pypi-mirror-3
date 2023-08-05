# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    pass

# OVERWRITE THIS VARIABLES WITH YOUR APIKEY
GOOGLE_APIKEY = "AIzaSyDDCHHwbfHLIsHWEhxAu41UmrRCg_Xmvm8"
MICROSOFT_APIKEY = "D9D0E326A70EA4E66218F43130890052808A0142"

def to_unicode(seq, enc):
    return [unicode(i, enc) for i in seq]

def to_encode(seq, enc):
    return [i.encode(enc) for i in seq]

def get_vim_variables():
    # settings from VimScript(.vimrc)
    try:
        api_name = vim.eval("raimei_api")
        lang_from = vim.eval("raimei_from")
        lang_to = vim.eval("raimei_to")
        enc = vim.eval("&enc")
    except vim.error:
        #  vim.error is String Exception
        print "Set enc, raimei_api, raimei_from, raimei_to variables!"
        raise
    return api_name, lang_from, lang_to, enc

def get_apikey(api_name):
    apikey = ""
    if api_name == "google":
        apikey = GOOGLE_APIKEY
    elif api_name == "microsoft":
        apikey = MICROSOFT_APIKEY
    return apikey

def get_translate_method(translater, api_name):
    api_method = lambda api, texts: (api, texts)
    if api_name == "google":
        api_method = translater.translate
    elif api_name == "microsoft":
        api_method = translater.translate_array
    return api_method
