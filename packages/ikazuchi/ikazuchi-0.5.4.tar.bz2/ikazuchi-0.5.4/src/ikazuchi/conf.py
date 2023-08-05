# -*- coding: utf-8 -*-

import ConfigParser
import os
from os.path import join as pathjoin

try:
    from ikazuchi.locale import _
except ImportError:
    def _(s): return s

CONF_DIR = u".ikazuchi"
CONF_FILE = u"ikazuchi.conf"
CONF_PATH = pathjoin(CONF_DIR, CONF_FILE)
SECTIONS = [
    ("general", ["http_proxy", "https_proxy"]),
    ("google", ["apikey"]),
    ("microsoft", ["apikey"]),
]

GOOGLE_APIKEY_REGISTER = "https://code.google.com/apis/console/"
MICROSOFT_APIKEY_REGISTER = "http://www.bing.com/developers"

def get_conf_path():
    """
    >>> get_conf_path().rsplit("/", 2)[-2:]
    [u'.ikazuchi', u'ikazuchi.conf']
    """
    import platform
    _os = platform.system()
    if _os == "Darwin" or _os == "Linux":
        prefix = os.getenv(u"HOME")
    elif _os == "Windows":
        prefix = os.getenv(u"APPDATA")
    return pathjoin(prefix, CONF_PATH)

def get_conf(conf_file):
    conf = ConfigParser.SafeConfigParser()
    has_conf_file = True
    if not os.access(conf_file, os.R_OK):
        create_conf_file(conf_file)
        has_conf_file = False
    conf.read(conf_file)
    get_or_set_sections(conf)
    # write conf file as template
    if not has_conf_file:
        with open(conf_file, "wb") as f:
            conf.write(f)
    return conf

def get_or_set_sections(conf):
    for section, options in SECTIONS:
        if not conf.has_section(section):
            conf.add_section(section)
        get_or_set_options(conf, section, options)

def get_or_set_options(conf, section, options):
    for option in options:
        try:
            conf.get(section, option)
        except ConfigParser.NoOptionError:
            conf.set(section, option, "")

def create_conf_file(conf_file):
    conf_dir = conf_file.rsplit("/", 1)[0]
    make_dirs(conf_dir)
    with open(conf_file, "wb") as f:
        pass  # menas touch command
    print _(u"created conf file: {0}".format(conf_file))

def make_dirs(path):
    if not os.access(path, os.F_OK):
        os.makedirs(path)
        print _(u"made directory: {0}".format(path))

def show_how_to_get_apikey():
    print _(u"You should get API KEY from each Translate API")
    print _(u"Google: {0}".format(GOOGLE_APIKEY_REGISTER))
    print _(u"Microsoft: {0}".format(MICROSOFT_APIKEY_REGISTER))
    print _(u"Set apikey = xxx in {0}".format(get_conf_path()))
    print _(u"")
