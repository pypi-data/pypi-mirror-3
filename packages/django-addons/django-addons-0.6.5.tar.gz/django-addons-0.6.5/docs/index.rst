
===========================
Django-addons documentation
===========================

Django-addons is a bunch of code that makes writing addon (or plugins, or
extensions) for your Django project much easier. Add 'django_addons' to your
Django project and then just drop all the addons in a subdirectory called
'addons' inside your project.

Features:

* Addons overview page
* Automatic signal connecting of addons
* Automatic URL discovery of addons
* Template hooking system (inject code from addons to your main project)
* 'django-staticfiles' to serve site media from each addon
* 'django-notifications' support (automatic registration of noticetypes)
* Per addon localization
* Per addon settings
* Disabling addons via ``./manage.py addons``


Tweaking your project
=====================

In order to take advantage of 'django-addons' you need to tweak your Django 
project a bit.


Settings
--------

First of all, you need to have some code in your settings to load the addons:

.. code-block:: python

    # Determines whether addon subsystem is enabled
    ENABLE_ADDONS = True

    # This is a list of paths where addons can be found
    ADDONS_ROOTS = [
        'addons'
    ]

    # Subset of INSTALLED_APPS
    ADDONS = []

    # Disabled addons are described in this file
    # You can use './manage.py addons' to enable and disable addons
    ADDONS_DISABLED_CONF = "disabled.conf"

    # In ADDONS_DISABLED_CONF file there should be only one var ADDONS_DISABLED
    ADDONS_DISABLED = []

    # Made sure we add the path into the PYTHONPATH in the correct order.
    ADDONS_ROOTS.reverse()

    # This piece of code scans ADDONS_ROOTS and register all found folders as 
    # Django applications. Directories that start with "." or end with 
    # ".disabled" are not registered
    for ADDONS_ROOT in ADDONS_ROOTS:
        # Checking for disabled addons
        file = os.path.abspath(os.path.join(ADDONS_ROOT, ADDONS_DISABLED_CONF))
        if os.path.isfile(file):
            execfile(file)

        # Lets add the ADDONS_ROOT path into the system PYTHONPATH.
        if not ADDONS_ROOT in sys.path:
            sys.path.insert(0, ADDONS_ROOT)

        for dir in sorted(os.listdir(ADDONS_ROOT)):
            if not dir in ADDONS_DISABLED and \
            os.path.isdir(os.path.join(ADDONS_ROOT, dir)) and \
            os.path.isfile(os.path.join(ADDONS_ROOT, dir, "__init__.py")):
                    if dir in ADDONS:
                        raise Exception("The addon '%s' is present in more " \
                                        "than one ADDONS_ROOT path." % dir)
                    ADDONS.append(dir)
                    if not dir in INSTALLED_APPS:
                        INSTALLED_APPS.append(dir)

                    # This allows doing magic like this in templates:
                    # <img src="{{STATIC_URL}}pluginName/image.png"> when
                    # image.png is located in /tx/addons/pluginName/media/image.png
                    if "STATICFILES_PREPEND_LABEL_APPS" in vars():
                        if not dir in STATICFILES_PREPEND_LABEL_APPS:
                            STATICFILES_PREPEND_LABEL_APPS.append(dir)

                    # Add addons' locale/ to the LOCALE_PATHS
                    if "LOCALE_PATHS" in vars():
                        if not isinstance( LOCALE_PATHS, tuple):
                            LOCALE_PATHS = LOCALE_PATHS,
                        LOCALE_PATHS += os.path.join(ADDONS_ROOT, dir, 'locale/'),

                    # Load settings/*.conf for each addon
                    confs = os.path.join(ADDONS_ROOT, dir, 'settings', '*.conf')
                    conffiles = glob.glob(confs)
                    conffiles.sort()
                    for f in conffiles:
                        execfile(os.path.abspath(f))

    ADDONS_PROVIDED = []


URLconf
-------

In your main ``urls.py`` you should include at the topmost level following piece
of code, so that addons could be able to override your project URLs. If you
don't want to allow your addons to override your URLs, just place it at the
bottom.

.. code-block:: python

    if settings.ENABLE_ADDONS:
        urlpatterns += patterns('', (r'', include('django_addons.urls')))


Debugging
---------

When debugging is enabled, django-addons enables a page under '/addons/' where
you can see status of each addon and some debugging information.


Developing addons
=================

Here's all you need to know to develop your own addons using this library.


Addon structure
---------------

Addon is basically a Django app living inside '<projectdir>/addons/' with a
structure as follows::

    <projectdir>/addons/example/__init__.py
    <projectdir>/addons/example/models.py
    <projectdir>/addons/example/views.py
    <projectdir>/addons/example/handlers.py
    <projectdir>/addons/example/locale/*/*.po
    <projectdir>/addons/example/settings/*.conf
    <projectdir>/addons/example/templates/*.html
    <projectdir>/addons/example/templatetags/*.py
    ...

Note that having a 'models.py' is important, even if it's empty. Also it's not
mandatory that the addons must live under '<projectdir>/addons/'. You can 
place it anyway it's convenient for your needs, even outside the '<projectdir>'.


Metainfo
--------

The file '<projectdir>/addons/example/__init__.py' should contain 
metaclass with information about the addon::

    class Meta:
        title = "About page for Project X"
        author = "John Smith"
        description = "Adds about page under /about"
        url = "/about"


Signals
-------

'<projectdir>/addons/example/handlers.py'::

    from projects.signals import blah
    def my_cool_handler():
        do_blah

    # NB! Django-Addons is looking for this function:
    def connect():
        blah.connect(my_cool_handler)


Template hooks
--------------

'<projectdir>/addons/example/templates/\*.html':

    These are templates that **can** overload your Django project templates.

'<projectdir>/addons/example/templates/example/additional_buttons.html':

    Addon-specific templates that **should not** overload your Django project
    templates. These can be included in your project code by:
    ``hook additional_buttons.html`` This way every file from each addon named
    'additional_buttons.html' will be merged together in your project templates.


Dependencies
------------

We suggest doing dependency checks in models.py::

    try:
        import Blah
    except ImportError:
        raise AddonError("You need Blah to use this addon.")


Overriding behavior
--------------------

Inserting hooks into the main project has a major drawback - for each hook
you lose significant amount of page loading time.

At this point we suggest using jQuery to modify default behavior
where it makes sense - for example to modify every item of a list.

Using jQuery to modify behavior implies that you should have consistent 'id'
attribute naming convention.

You can for example load your jQuery code in the head segment and actually
insert buttons, tabs etc. using the JS code itself.


Internationalization
--------------------

To internationalize your addon go to '<projectdir>/addon/example' and run::

    django-admin.py makemessages --all

To generate ``.mo`` files for the whole project in '<projectdir>' run::

    ./manage.py compilemessages


Issues
======

Signal execution order is not determined. Solution: Addons can emit their own
signals and other addons can catch them to determine the order of execution.
Signal dependencies -> Addon dependencies. The solution on the main project
side is to provide signals for each small step so the addon would register
themselves at the most logical point. With step-by-step signals there is no
need to trap a part of  your Django project code in addon to control it's
behavior.

Conclusion: ordering of addons is out of the scope of addon subsystem. If
addon1 handler needs addon2 handler  to run first, then addon1 developer just
includes it in their package and django-addons does not care about this.


Coding tips
===========

Instead of importing models directly we strongly suggest using the
``get_model()`` function provided by Django, which will probably save you from
other issues as well.

For example, let's say you want to access your addon model from your addon
template tags. Here's how you should do it:

    from django.db.models import get_model
    MyModel = get_model('addon_name', 'MyModel')

The 'obvious' way (with all the problems it might have) is the following, which
should be **avoided**::

    from full.prefix.to.addons.addon_name.models import MyModel


Disabling addons
----------------

By default all addons dropped in ``ADDONS_ROOT`` directory are enabled.
You can optionally disable addons via the management command 'addons'::

    # list addons
    ./manage.py addons

    # enable addon
    ./manage.py addons -e ADDON_NAME

    # disable addon
    ./manage.py addons -d ADDON_NAME

Information about disabled addons will be stored in ``ADDONS_ROOT/disabled.conf``.


django-staticfiles
------------------

We're using `django-staticfiles <http://bitbucket.org/jezdez/django-staticfiles>`_
to serve the 'media' folder from each addon root.

Lets say you have 'image.png' in '<projectdir>/addons/MyPlugin/media/image.png'.
In the templates you can do something like this (be careful with slashes!):

.. code-block:: html

    <img src="{{ STATIC_URL }}myPlugin/image.png"/>

If you have ``DEBUG = True``, the URLconf does it's magic and everything works
fine without copying file.  Note that this is not secure way to serve files.
For real-life deployment you should set ``DEBUG = False`` and run the command::

    ./manage.py build_static 

Note that after you have installed 'django-staticfiles', you should have
something like this in your Django project's settings.

.. code-block:: python
 
    # The absolute path to the directory that holds static files
    STATIC_ROOT = os.path.join(PROJECT_PATH, 'static_media/static')

    # URL that handles the files served from STATIC_ROOT
    STATIC_URL = '/static_media/static/'
 
    # A sequence of directory names to be used when searching for media files
    # in installed apps, e.g. if an app has its media files in <app>/media use
    STATICFILES_MEDIA_DIRNAMES = ('media',)
 
    # A sequence of app paths that should be prefixed with the label name.
    # For example, django.contrib.admin media files should be served from
    # admin/[js,css,images] rather than the media files getting served directly
    # from the static root.
    STATICFILES_PREPEND_LABEL_APPS = []


django-notification
-------------------

We have implemented an autodiscover function for
`django-notification <http://github.com/jtauber/django-notification/>`_ which
looks for 'notifications.py' in each addon root.

'<projectdir>/addons/notifications.py':

.. code-block:: python

    # This is the suggested way of doing thing at the moment
    # We'll probably move to signal based architecture once django-notification
    # guys will add the features what we need to make it happen
    from common.notifications import NOTICE_TYPES
    NOTICE_TYPES += [ blah ]

TODO
====

* Dynamic addon loading using django.db.models.loading.load_app
* Use django.db.models.loading.get_apps to get list of loaded addons
* Addon dependency checking
* Better hooking system
* Better loading for the settings file. Ideally we should ask the developer to
  just exec() a particular file in his 'addons' directory.

