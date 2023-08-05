# -*- coding: utf-8 -*-

from pkg_resources import (iter_entry_points, load_entry_point)
from ikazuchi.core.handler import NullHandler

try:
    from ikazuchi.locale import _
except ImportError:
    def _(s): return s

def get_plugin(opts):
    p = load_plugin(opts.plugin)
    translator = p.Translator if hasattr(p, "Translator") else None
    handler = p.Handler if hasattr(p, "Handler") else None
    try:
        handler_instance = handler(opts)
    except Exception as err:
        handler_instance = NullHandler()
        print _(u"Cannot instantiate Handler: {0}".format(err))
    return translator, handler_instance

def get_plugin_name(group="ikazuchi.plugins"):
    return [entry_point.name for entry_point in iter_entry_points(group)]

def get_plugin_distribution(name, group="ikazuchi.plugins"):
    for entry_point in iter_entry_points(group):
        if entry_point.name == name:
            return entry_point.dist

def load_plugin(name, group="ikazuchi.plugins"):
    dist = get_plugin_distribution(name)
    plugin = None
    try:
        plugin = dist.load_entry_point(group, name)
    except (ImportError, TypeError, ValueError) as err:
        print _(u"Load plugin error:")
        print _(u"  distribution: {0}".format(dist))
        print _(u"  group name  : {0}".format(group))
        print _(u"  plugin name : {0}".format(name))
        print _(u"  messages    : {0}".format(err))
    return plugin

def load_all_plugins(group="ikazuchi.plugins"):
    plugins = []
    for entry_point in iter_entry_points(group):
        try:
            plugins.append(entry_point.load())
        except ImportError as err:
            print "Load plugin error: {0}".format(err)
    return plugins
