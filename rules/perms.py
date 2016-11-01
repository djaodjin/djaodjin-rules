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

import json, logging, urlparse
from importlib import import_module
from itertools import izip

from django.conf import settings as django_settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.utils.module_loading import import_string

from . import settings
from .models import Rule


LOGGER = logging.getLogger(__name__)


def _insert_url(request, redirect_field_name=REDIRECT_FIELD_NAME,
                inserted_url=None):
    '''Redirects to the *inserted_url* before going to the orginal
    request path.'''
    # This code is pretty much straightforward
    # from contrib.auth.user_passes_test
    path = request.build_absolute_uri()
    # If the login url is the same scheme and net location then just
    # use the path as the "next" url.
    login_scheme, login_netloc = urlparse.urlparse(inserted_url)[:2]
    current_scheme, current_netloc = urlparse.urlparse(path)[:2]
    if ((not login_scheme or login_scheme == current_scheme) and
        (not login_netloc or login_netloc == current_netloc)):
        path = request.get_full_path()
    # As long as *inserted_url* is not None, this call will redirect
    # anything (i.e. inserted_url), not just the login.
    from django.contrib.auth.views import redirect_to_login
    return redirect_to_login(path, inserted_url, redirect_field_name)


def _get_full_page_path(page_path):
    path_prefix = ""
    if not page_path.startswith("/"):
        page_path = "/" + page_path
    if settings.PATH_PREFIX_CALLABLE:
        path_prefix = import_string(settings.PATH_PREFIX_CALLABLE)()
        if path_prefix and not path_prefix.startswith("/"):
            path_prefix = "/" + path_prefix
    return "%s%s" % (path_prefix, page_path)


def _load_func(path):
    """
    Load a function from its path as a string.
    """
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
    return func


def _find_rule(request, app):
    """
    Returns a tuple mad of the rule that was matched and a dictionnary
    of parameters that where extracted from the URL (i.e. :slug).
    """
    params = {}
    request_path = request.path
    parts = [part for part in request_path.split('/') if part]
    for rule in app.get_rules():
        page_path = _get_full_page_path(rule.path)
        LOGGER.debug("Match %s with %s ...", request_path, page_path)
        # Normalize to avoid issues with path starting or ending with '/':
        pat_parts = [part for part in page_path.split('/') if part]
        if len(parts) >= len(pat_parts):
            # Only worth matching if the URL is longer than the pattern.
            try:
                params = json.loads(rule.kwargs)
            except ValueError:
                params = {}
            matched = rule
            for part, pat_part in izip(parts, pat_parts):
                if pat_part.startswith(':'):
                    slug = pat_part[1:]
                    if slug in params:
                        params.update({slug: part})
                elif part != pat_part:
                    matched = None
                    break
            if matched:
                LOGGER.debug(
                    "matched %s with %s (rule=%d, forward=%s, params=%s)",
                    request_path, page_path,
                    matched.rule_op, matched.is_forward,
                    params)
                return (matched, params)
    return (None, {})



def check_permissions(request, app, redirect_field_name=REDIRECT_FIELD_NAME,
                      login_url=None):
    session = {}
    matched, params = _find_rule(request, app)
    if matched:
        # We will need manager relations and subscriptions in
        # almost all cases, so let's just load all of it here.
        if request.user.is_authenticated():
            #pylint: disable=no-member
            serializer_class = import_string(settings.SESSION_SERIALIZER)
            serializer = serializer_class(request.user)
            session = serializer.data
        if matched.rule_op == Rule.ANY:
            return (None, matched.is_forward, session)
        else:
            if not request.user.is_authenticated():
                LOGGER.debug("user is not authenticated")
                return (_insert_url(request, redirect_field_name,
                    login_url or django_settings.LOGIN_URL), False, session)
            fail_func = _load_func(
                settings.RULE_OPERATORS[matched.rule_op][1])
            LOGGER.debug("calling %s(user=%s, params=%s) ...",
                fail_func.__name__, request.user, params)
            redirect = fail_func(request, **params)
            LOGGER.debug("calling %s(user=%s, params=%s) => %s",
                fail_func.__name__, request.user, params, redirect)
            if redirect:
                content_type = request.META.get('CONTENT_TYPE', '')
                if (content_type.lower() in ['text/html', 'text/plain']
                    and isinstance(redirect, basestring)):
                    return (_insert_url(
                        request, redirect_field_name, redirect), False, session)
                LOGGER.debug("Content-Type: '%s' looks like an API call "\
                    "=> PermissionDenied", content_type)
                raise PermissionDenied
            return (None, matched.is_forward, session)
    LOGGER.debug("unmatched %s", request.path)
    raise PermissionDenied
