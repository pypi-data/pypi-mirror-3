# -*- coding: utf-8 -*-
from django.db.models.signals import *
"""

This is a simple addon which just dumps information 
about signals passed in your Django project.

Sample output:

Example addon received SIGNAL:
              sender = <class 'projects.models.Project'>,
                 raw = False,
            instance = some-cool-project,
             created = False

"""

def handler(sender, signal=None, **kwargs):
    s = []
    for key, value in (("sender", sender),):
        s += ["\t% 12s = %s" % (key,value)]
    for key, value in kwargs.iteritems():
        if key != "request":
            s += ["\t% 12s = %s" % (key,value)]
        else:
           s += ["\t% 12s = %s" % ("request","<skipped>")]
           s += ["\t% 12s = %s" % ("request.POST",value.POST)]
           s += ["\t% 12s = %s" % ("request.GET", value.GET)]
    print "Example addon received SIGNAL:\n%s" % (',\n'.join(s))

# Django signals:
for signal in [
    post_save,
    post_delete,]:
    signal.connect(handler)

