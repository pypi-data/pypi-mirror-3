# -*- coding: utf-8 -*-

"""
This is django_addons.urls module, it loads URLconf of
each addon.

In main urls you should have something like:

  urlpatterns += patterns('', (r'', include('django_addons.urls')))


Copyright (C) 2010 by Indifex (www.indifex.com), see AUTHORS.
License: BSD, see LICENSE for details.

For further information visit http://code.indifex.com/django-addons

"""

import os
from django.conf.urls.defaults import *
from django.conf import settings
from views import addons_view

urlpatterns = patterns('')

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^addons/$', addons_view))

for addon in settings.ADDONS:
    addon_dir = None
    for ADDONS_ROOT in settings.ADDONS_ROOTS:
        addon_dir = "%s/%s" % (ADDONS_ROOT, addon)
        if os.path.exists(addon_dir):
            break

    filename = "%s/urls.py" % (addon_dir)
    fullname = "%s.urls" % addon
    if os.path.exists(filename):
        urlpatterns += patterns('',
            url(r'', include(fullname)),
        )
