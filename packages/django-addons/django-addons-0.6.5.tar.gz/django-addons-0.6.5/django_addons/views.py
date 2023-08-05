# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 by Indifex (www.indifex.com), see AUTHORS.
License: BSD, see LICENSE for details.

For further information visit http://code.indifex.com/django-addons
"""

from django.db import models
from django.conf import settings
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response #, get_object_or_404
from django.template import RequestContext

from django_addons import get_meta

def addons_view(request):
    addons = {}
    for addon in settings.ADDONS:
        print addon
        addons[addon] = dict()
        addons[addon]["meta"] = get_meta(addon)
        addons[addon]["enabled"] = True
        
        m = "%s.models" % addon
        for app in models.get_apps():
            if m == app.__name__:
                addons[addon]["models_loaded"] = True
                break

    for addon in settings.ADDONS_DISABLED:
        addons[addon] = dict()
        addons[addon]["meta"] = get_meta(addon)
        addons[addon]["enabled"] = False
        
    context = {"addons":addons, "settings":settings }
    return render_to_response("addons.html", context,
        context_instance=RequestContext(request))
