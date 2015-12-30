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

import datetime

from django.utils.timezone import utc

from . import settings


def datetime_or_now(dtime_at=None):
    if not dtime_at:
        return datetime.datetime.utcnow().replace(tzinfo=utc)
    if dtime_at.tzinfo is None:
        dtime_at = dtime_at.replace(tzinfo=utc)
    return dtime_at

#pylint: disable=invalid-name

try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError: # django < 1.8
    #pylint: disable=unused-import
    from django.db.models.loading import get_model


def get_model_class(full_name, settings_meta):
    """
    Returns a model class loaded from *full_name*. *settings_meta* is the name
    of the corresponding settings variable (used for error messages).
    """
    from django.core.exceptions import ImproperlyConfigured

    try:
        app_label, model_name = full_name.split('.')
    except ValueError:
        raise ImproperlyConfigured(
            "%s must be of the form 'app_label.model_name'" % settings_meta)
    model_class = get_model(app_label, model_name)
    if model_class is None:
        raise ImproperlyConfigured(
            "%s refers to model '%s' that has not been installed"
            % (settings_meta, full_name))
    return model_class


if isinstance(settings.ACCOUNT_MODEL, str):
    Account = get_model_class(settings.ACCOUNT_MODEL, 'ACCOUNT_MODEL')
else:
    Account = settings.ACCOUNT_MODEL


try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User #pylint: disable=unused-import
else:
    User = get_user_model()
