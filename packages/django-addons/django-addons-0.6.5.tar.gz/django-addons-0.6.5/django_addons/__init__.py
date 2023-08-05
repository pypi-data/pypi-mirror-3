# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 by Indifex (www.indifex.com), see AUTHORS.
License: BSD, see LICENSE for details.

For further information visit http://code.indifex.com/django-addons
"""

import os
import sys

VERSION = (0, 6, 5, 'final')

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != 'final':
        version = '%s %s' % (version, VERSION[3])
    return version

def dependency_found(addon):
    from django.conf import settings
    return addon in ( \
        getattr(settings, "ADDONS", []) + 
        getattr(settings, "ADDONS_PROVIDED", []))

def get_meta(name):
    # Load metainformation
    try:
        mod = None
        __import__(name)
        mod = sys.modules[name]
    except Exception, e:
        print e
        pass
    return getattr(mod, 'Meta', None)



