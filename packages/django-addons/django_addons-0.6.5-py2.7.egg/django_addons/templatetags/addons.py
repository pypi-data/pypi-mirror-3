# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 by Indifex (www.indifex.com), see AUTHORS.
License: BSD, see LICENSE for details.

For further information visit http://code.indifex.com/django-addons
"""

import re
from django import template
from django.conf import settings
from django.template import Node, Variable, TemplateSyntaxError, TemplateDoesNotExist
from django.template.loader import get_template_from_string
from django.template.loader_tags import BlockNode

# Backwards compatibility with Django 1.1
try:
    from django.template.loader import find_template
except ImportError:
    from django.template.loader import find_template_source as find_template

"""
This module adds support for hook tag which allows doing magic like this:

In your Django project define a piece of page which imports some stuff from *all* addons:
/MyDjangoProject/templates/main.html

  {% load addons %}
  <ul>
  <li>Menuitem 1</li>
  <li>Menuitem 2</li>
  {% hook "main.html" navmenu %}
  </ul>

In a addon define: 
/MyDjangoProject/addons/MyAddon/templates/MyAddon/main.html:
  {% block navmenu %}
  <li>Custom menuitem</li>
  {% endblock }

In some other addon define:
/MyDjangoProject/addons/MyOtherAddon/templates/MyOtherAddon/main.html:
  {% block navmenu %}
  <li>Other menuitem</li>
  {% endblock }

This all ends up rendered as:

  <ul>
  <li>Menuitem 1</li>
  <li>Menuitem 2</li>
  <li>Custom menuitem</li>
  <li>Other menuitem</li>
  </ul>

Rendering order depends on the addon directory names.
Directory /MyDjangoProject/addons is read, sorted and then appended to INSTALLED_APPS.
To force ordering you can prepend addon directories with numbers like this:

  /MyDjangoProject/addons/01_MyOtherAddon
  /MyDjangoProject/addons/02_MyAddon

NB! For the addon directory name under templates/ has to be same as directory name under addons/ 

"""

register = template.Library()

# It would be to heavy to load template again for each node
template_cache = {}

class HookNode(Node):
    def __init__(self, nodelist, template, block_name):
        if nodelist:
            self.nodelist = nodelist
        self.template = template
        self.block_name = block_name

    def render(self, context):
        if not settings.ENABLE_ADDONS:
            return ""
        template = self.template
        retval = ""

        for addon in settings.ADDONS:
            path = "%s/%s" % (addon, template)
            if path in template_cache:                
                addon_template = template_cache[path]

            else:
                try:
                    source, origin = find_template(path)
                    addon_template = get_template_from_string(source, origin, template)
                    template_cache[path] = addon_template
                except TemplateDoesNotExist:
                    addon_template = None
                    template_cache[path] = None
                
            if addon_template:
                # Block is not defined, include whole file
                #print "Block not defined, including whole file..."
                if not self.block_name:
                    retval += addon_template.render(context)
                # Block is defined so look up for the block in the template
                else:
                    for node in addon_template.nodelist:
                        if isinstance(node, BlockNode) and \
                            node.name == self.block_name:
                            #print "Inserting node %s from file..." % self.block_name
                            retval += node.render(context)
        # We didn't include anything - keep parent's content
        if retval == "":
            if hasattr(self, "nodelist"):
                return self.nodelist.render(context)
        else:
            return retval
        return ""

def do_hook(parser, token):
     bits = token.split_contents()
     tag = bits[0]
     if len(bits) < 2 or len(bits) > 3:
         raise TemplateSyntaxError, "%r tag arguments are: template [block_name]" % tag
     template = bits[1]
     try:
         _,_,block_name = bits
     except:
         block_name = None

     if template[0] in ('"', "'") and template[-1] == template[0]:
         template = template[1:-1] # Strip quotes
     else:
         raise TemplateSyntaxError, "%r tag requires 'template' argument to be quoted" % tag

     #regexp = "[^A-Za-z0-9_-]" # Do not allow including /etc/passwd or something like that
     #if re.search(regexp, addon_name) == None:

     if tag == "hookblock":
         nodelist = parser.parse(('endhookblock',))
         parser.delete_first_token()
     else:
         nodelist = None
     return HookNode(nodelist, template, block_name)

register.tag('hook', do_hook)
register.tag('hookblock', do_hook)
