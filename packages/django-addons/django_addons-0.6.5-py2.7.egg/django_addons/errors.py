# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 by Indifex (www.indifex.com), see AUTHORS.
License: BSD, see LICENSE for details.

For further information visit http://code.indifex.com/django-addons
"""

class AddonIncompatible(Exception):
    """
    This should be thrown when addon wants to import
    something from the base Django project but can't find it.

    This usually should indicate that addon has been installed onto
    wrong Django project
    """
    pass

class AddonError(StandardError):
    """
    Base class for all addon errors.
    """
    pass
