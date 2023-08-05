# -*- coding: utf-8 -*-

import ConfigParser
import os
from nose.tools import *
from os.path import (dirname, join as pathjoin)

# functions for test
from ikazuchi.conf import *

def _assert(expected, actual):
    assert_equal(expected, actual)

class TestExistingConfigFile(object):

    conf_file = pathjoin(dirname(__file__), "data/conf/ikazuchi.conf")

    def test_get_conf(self):
        expected = {
            "general": {"http_proxy": "localhost:8080",
                        "https_proxy": "localhost:8080"},
            "google": {"apikey": "xxx"},
            "microsoft": {"apikey": "yyy"},
        }
        conf = get_conf(self.conf_file)
        for section, options in SECTIONS:
            for opt in options:
                yield _assert, expected[section][opt], conf.get(section, opt)


class TestNotExistingConfigFile(object):

    conf_file = pathjoin(dirname(__file__), "data/conf/notexisting.conf")

    def setup(self):
        self._remove_conf()

    def teardown(self):
        self._remove_conf()

    def _remove_conf(self):
        if os.access(self.conf_file, os.R_OK):
            os.remove(self.conf_file)

    def test_get_conf(self):
        expected = {
            "general": {"http_proxy": "", "https_proxy": ""},
            "google": {"apikey": ""},
            "microsoft": {"apikey": ""},
        }
        conf = get_conf(self.conf_file)
        for section, options in SECTIONS:
            for opt in options:
                yield _assert, expected[section][opt], conf.get(section, opt)

    def test_create_conf_file(self):
        yield _assert, False, os.access(self.conf_file, os.R_OK)
        create_conf_file(self.conf_file)
        yield _assert, True, os.access(self.conf_file, os.R_OK)

    def test_get_or_set_sections(self):
        conf = ConfigParser.SafeConfigParser()
        get_or_set_sections(conf)
        _assert([s[0] for s in SECTIONS], conf.sections())

    def test_get_or_set_options(self):
        conf = ConfigParser.SafeConfigParser()
        expected = {
            "general": [("http_proxy", ""), ("https_proxy", "")],
            "google": [("apikey", "")],
            "microsoft": [("apikey", "")],
        }
        get_or_set_sections(conf)
        for section, options in SECTIONS:
            get_or_set_options(conf, section, options)
            yield _assert, expected[section], conf.items(section)
