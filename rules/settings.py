# Copyright (c) 2015, DjaoDjin inc.
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

from django.conf import settings

_SETTINGS = {
    'ACCOUNT_MODEL': getattr(settings, 'AUTH_USER_MODEL', None),
    'DEFAULT_APP_CALLABLE': None,
    'DEFAULT_APP_ID': getattr(settings, 'SITE_ID', 1),
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

RULES_APP_MODEL = getattr(settings, 'RULES_APP_MODEL', 'rules.App')

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
ACCOUNT_MODEL = _SETTINGS.get('ACCOUNT_MODEL')
DEFAULT_APP_CALLABLE = _SETTINGS.get('DEFAULT_APP_CALLABLE')
DEFAULT_APP_ID = _SETTINGS.get('DEFAULT_APP_ID')
PATH_PREFIX_CALLABLE = _SETTINGS.get('PATH_PREFIX_CALLABLE')
RULE_OPERATORS = _SETTINGS.get('RULE_OPERATORS')
SESSION_SERIALIZER = _SETTINGS.get('SESSION_SERIALIZER')

DB_RULE_OPERATORS = tuple([(idx, item[0])
                           for idx, item in enumerate(RULE_OPERATORS)])

# We would use:
#     from django.core.validators import slug_re
#     SLUG_RE = slug_re.pattern
# but that includes ^ and $ which makes it unsuitable for use in URL patterns.
SLUG_RE = r'[a-zA-Z0-9_\-]+'
