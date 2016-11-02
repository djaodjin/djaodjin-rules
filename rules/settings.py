# Copyright (c) 2016, DjaoDjin inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Convenience module for access of rules application settings,
which enforces default settings when the main settings module
does not contain the appropriate settings.
"""
import inspect
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


_SETTINGS = {
    'ACCOUNT_MODEL': getattr(settings, 'AUTH_USER_MODEL', None),
    'ACCOUNT_URL_KWARG': None,
    'DEFAULT_APP_CALLABLE': None,
    'DEFAULT_APP_ID': getattr(settings, 'SITE_ID', 1),
    'DEFAULT_RULES': [('/', 0, False)],
    'ENGAGED_TRIGGERS': tuple([]),
    'EXTRA_MIXIN': object,
    'PATH_PREFIX_CALLABLE': None,
    'RULE_OPERATORS': (
        ('Any',
         ''),
        ('Authenticated',
         'django.contrib.auth.decorators.login_required'),
    ),
    'SESSION_SERIALIZER': 'rules.api.serializers.UserSerializer'
}
_SETTINGS.update(getattr(settings, 'RULES', {}))


def _load_perms_func(path):
    """
    Load a function from its path as a string.
    """
    if not path:
        return "Any", None, {}
    if callable(path):
        func = path
    elif isinstance(path, basestring):
        dot_pos = path.rfind('.')
        module, attr = path[:dot_pos], path[dot_pos + 1:]
        try:
            mod = import_module(module)
        except ImportError as err:
            raise ImproperlyConfigured('Error importing %s: "%s"'
                % (path, err))
        except ValueError:
            raise ImproperlyConfigured('Error importing %s: ' % path)
        try:
            func = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s"'
                % (module, attr))
    else:
        raise ImproperlyConfigured(
            '%s is neither callable or a module path' % path)

    short_name = ""
    for line in func.__doc__.splitlines():
        short_name = line.strip()
        if len(short_name) > 0:
            break
    if not short_name:
        raise ImproperlyConfigured(
            '%s should have at least a one-line documentation' % path)

    argspec = inspect.getargspec(func)
    flags = len(argspec.args)
    if argspec.defaults:
        flags = len(argspec.args) - len(argspec.defaults)
    parms = {}
    for arg in argspec.args[flags:]:
        parms.update({arg: ""})

    return short_name, func, parms


RULES_APP_MODEL = getattr(settings, 'RULES_APP_MODEL', 'rules.App')

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
ACCOUNT_MODEL = _SETTINGS.get('ACCOUNT_MODEL')
ACCOUNT_URL_KWARG = _SETTINGS.get('ACCOUNT_URL_KWARG')
DEFAULT_APP_CALLABLE = _SETTINGS.get('DEFAULT_APP_CALLABLE')
DEFAULT_APP_ID = _SETTINGS.get('DEFAULT_APP_ID')
DEFAULT_RULES = _SETTINGS.get('DEFAULT_RULES')
ENGAGED_TRIGGERS = _SETTINGS.get('ENGAGED_TRIGGERS')
EXTRA_MIXIN = _SETTINGS.get('EXTRA_MIXIN')
PATH_PREFIX_CALLABLE = _SETTINGS.get('PATH_PREFIX_CALLABLE')
RULE_OPERATORS = tuple([_load_perms_func(item)
    for item in _SETTINGS.get('RULE_OPERATORS')])
SESSION_SERIALIZER = _SETTINGS.get('SESSION_SERIALIZER')

DB_RULE_OPERATORS = tuple([(idx, item[0])
    for idx, item in enumerate(RULE_OPERATORS)])

# We would use:
#     from django.core.validators import slug_re
#     SLUG_RE = slug_re.pattern
# but that includes ^ and $ which makes it unsuitable for use in URL patterns.
SLUG_RE = r'[a-zA-Z0-9_\-]+'
