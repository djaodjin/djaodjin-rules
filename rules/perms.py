# Copyright (c) 2017, DjaoDjin inc.
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

import logging, urlparse

from django.conf import settings as django_settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.utils.module_loading import import_string

from . import settings
from .models import Rule


LOGGER = logging.getLogger(__name__)


class NoRuleMatch(RuntimeError):

    def __init__(self, path):
        super(NoRuleMatch, self).__init__(
            u"No access rules triggered by path '%s'" % unicode(path))


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


def _get_accept_list(request):
    http_accept = request.META.get('HTTP_ACCEPT', '*/*')
    return [item.strip() for item in http_accept.split(',')]


def find_rule(request, app, prefixes=None):
    """
    Returns a tuple mad of the rule that was matched and a dictionnary
    of parameters that where extracted from the URL (i.e. :slug).
    """
    matched_rule = getattr(request, 'matched_rule', None)
    matched_params = getattr(request, 'matched_params', {})
    if matched_rule:
        # Use cached tuple.
        return (matched_rule, matched_params)
    params = {}
    request_path = request.path
    request_path_parts = [part for part in request_path.split('/') if part]
    for rule in app.get_rules(prefixes=prefixes):
        LOGGER.debug("Match %s with %s ...",
            '/'.join(request_path_parts), rule.get_full_page_path())
        params = rule.match(request_path_parts)
        if params is not None:
            LOGGER.debug(
                "matched %s with %s (rule=%d, forward=%s, params=%s)",
                request_path, rule.get_full_page_path(),
                rule.rule_op, rule.is_forward, params)
            return (rule, params)
    return (None, {})


def redirect_or_denied(request, inserted_url,
                       redirect_field_name=REDIRECT_FIELD_NAME, descr=None):
    http_accepts = _get_accept_list(request)
    if ('text/html' in http_accepts
        and isinstance(inserted_url, basestring)):
        return _insert_url(request,
            redirect_field_name=redirect_field_name, inserted_url=inserted_url)
    LOGGER.debug("Looks like an API call or no inserted url"\
        " (Accept: '%s', insert='%s') => PermissionDenied",
        request.META.get('HTTP_ACCEPT', '*/*'), inserted_url)
    if descr is None:
        descr = ""
    raise PermissionDenied(descr)


def fail_rule(request, rule, params, redirect_field_name=REDIRECT_FIELD_NAME,
              login_url=None):
    if not request.user.is_authenticated():
        LOGGER.debug("user is not authenticated")
        return _insert_url(request, redirect_field_name,
            login_url or django_settings.LOGIN_URL)
    _, fail_func, defaults = settings.RULE_OPERATORS[rule.rule_op]
    kwargs = defaults.copy()
    if isinstance(params, dict):
        kwargs.update(params)
    LOGGER.debug("calling %s(user=%s, kwargs=%s) ...",
        fail_func.__name__, request.user, kwargs)
    redirect = fail_func(request, **kwargs)
    LOGGER.debug("calling %s(user=%s, kwargs=%s) => %s",
        fail_func.__name__, request.user, kwargs, redirect)
    if redirect:
        return redirect_or_denied(request, redirect, redirect_field_name)
    return None


def check_matched(request, app, prefixes=None,
                  redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Returns a tuple (response, forward, session) if the *request.path* can
    be matched otherwise raises a NoRuleMatch exception.
    """
    session = {}
    matched, params = find_rule(request, app, prefixes=prefixes)
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
            response = fail_rule(request, matched, params, login_url=login_url,
                redirect_field_name=redirect_field_name)
            return (response,
                matched.is_forward if response is None else False, session)
    LOGGER.debug("unmatched %s", request.path)
    raise NoRuleMatch(request.path)


def check_permissions(request, app, redirect_field_name=REDIRECT_FIELD_NAME,
                      login_url=None):
    """
    Returns a tuple (response, forward, session) if the *request.path* can
    be matched otherwise raises a PermissionDenied exception.
    """
    try:
        return check_matched(request, app,
            redirect_field_name=redirect_field_name, login_url=login_url)
    except NoRuleMatch as err:
        raise PermissionDenied(str(err))
