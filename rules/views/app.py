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

import json, logging, re, urlparse
from importlib import import_module
from itertools import izip

from django.conf import settings as django_settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages
from django.contrib.sites.requests import RequestSite
from django.core.exceptions import (FieldError, ImproperlyConfigured,
    PermissionDenied)
from django.http import HttpResponse
from django.http.cookie import SimpleCookie
from django.utils.module_loading import import_string
from django.views.generic import UpdateView, TemplateView
import requests
from requests.exceptions import RequestException
from deployutils.backends.encrypted_cookies import SessionStore
from deployutils.settings import SESSION_COOKIE_NAME

from .. import settings
from ..compat import get_model
from ..mixins import AppMixin
from ..models import App, Rule


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


class SessionProxyMixin(AppMixin):
    """
    Proxy to the application

    Check permissions associated to the request and forwards request
    when appropriate.
    """
    # Implementation Note:
    # We cannot override ``dispatch()`` because djangorestframework happens
    # to do user authentication there.

    redirect_field_name = REDIRECT_FIELD_NAME
    login_url = None

    @property
    def session_cookie_string(self):
        """
        Return the encrypted session information
        added to the HTTP Cookie Headers.
        """
        if not hasattr(self, '_session_cookie_string'):
            session_store = SessionStore(self.app.enc_key)
            self._session_cookie_string = session_store.prepare(
                self.session, self.app.enc_key)
        return self._session_cookie_string

    @staticmethod
    def get_full_page_path(page_path):
        path_prefix = ""
        if settings.PATH_PREFIX_CALLABLE:
            path_prefix = import_string(settings.PATH_PREFIX_CALLABLE)()
        return '/%s%s' % (path_prefix, page_path)

    def find_rule(self, request):
        """
        Returns a tuple mad of the rule that was matched and a dictionnary
        of parameters that where extracted from the URL (i.e. :slug).
        """
        params = {}
        request_path = request.path
        parts = [part for part in request_path.split('/') if part]
        for rule in self.app.get_rules():
            page_path = self.get_full_page_path(rule.path)
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

    def check_permissions(self, request):
        self.session = {}
        matched, params = self.find_rule(request)
        if matched:
            # We will need manager relations and subscriptions in
            # almost all cases, so let's just load all of it here.
            if request.user.is_authenticated():
                #pylint: disable=no-member
                serializer_class = import_string(
                    settings.SESSION_SERIALIZER)
                serializer = serializer_class(request.user)
                self.session = serializer.data
            if matched.rule_op == Rule.ANY:
                return (None, matched.is_forward)
            else:
                if not request.user.is_authenticated():
                    LOGGER.debug("user is not authenticated")
                    return (_insert_url(
                        request, self.redirect_field_name,
                        self.login_url or django_settings.LOGIN_URL),
                        False)
                fail_func = _load_func(
                    settings.RULE_OPERATORS[matched.rule_op][1])
                redirect = fail_func(request, **params)
                if redirect:
                    content_type = request.META.get('CONTENT_TYPE', '')
                    if (content_type.lower() in ['text/html', 'text/plain']
                        and isinstance(redirect, basestring)):
                        return (_insert_url(
                            request, self.redirect_field_name, redirect), False)
                    raise PermissionDenied
                return (None, matched.is_forward)
        LOGGER.debug("unmatched %s", request.path)
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(SessionProxyMixin, self).get_context_data(**kwargs)
        line = "%s: %s" % (SESSION_COOKIE_NAME, self.session_cookie_string)
        context.update({'forward_session': json.dumps(self.session, indent=2),
            'forward_session_cookie': '\\\n'.join(
            [line[i:i+48] for i in range(0, len(line), 48)])})
        return context

    def get(self, request, *args, **kwargs):
        response = self.conditional_forward(request)
        if response:
            return response
        return super(SessionProxyMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = self.conditional_forward(request)
        if response:
            return response
        return super(SessionProxyMixin, self).post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        response = self.conditional_forward(request)
        if response:
            return response
        return super(SessionProxyMixin, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        response = self.conditional_forward(request)
        if response:
            return response
        return super(SessionProxyMixin, self).patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        response = self.conditional_forward(request)
        if response:
            return response
        return super(SessionProxyMixin, self).delete(request, *args, **kwargs)

    def conditional_forward(self, request):
        response, forward = self.check_permissions(request)
        if response:
            return response
        if forward:
            try:
                return self.fetch_remote_page()
            except RequestException as err:
                if 'text/html' in request.META.get('HTTP_ACCEPT'):
                    messages.error(
                        request, 'Unable to forward request. %s' % err)
        return None

    def fetch_remote_page(self):
        """
        Forward the request to the remote site after adjusting session
        information and request headers.

        Respond with the remote site response after adjusting session
        information and response headers.
        """
        remoteurl = '%s%s' % (self.app.entry_point, self.request.path)
        requests_args = self.translate_request_args(self.request)
        LOGGER.debug("%s %s with session %s, updated headers: %s",
            self.request.method, remoteurl, self.session, requests_args)
        response = requests.request(
            self.request.method, remoteurl, **requests_args)
        return self.translate_response(response)


    def translate_request_args(self, request):
        requests_args = {'allow_redirects': False, 'headers': {}}
        cookies = SimpleCookie()
        for key, value in request.COOKIES.items():
            cookies[key] = value
        if self.app.forward_session:
            cookies[SESSION_COOKIE_NAME] = self.session_cookie_string
        #pylint: disable=maybe-no-member
        cookie_string = cookies.output(header='', sep='; ')

        # Retrieve the HTTP headers from a WSGI environment dictionary.  See
        # https://docs.djangoapp.com/en/dev/ref/request-response/\
        #    #django.http.HttpRequest.META
        headers = {}
        for key, value in request.META.iteritems():
            key_upper = key.upper()
            if key_upper.startswith('HTTP_'):
                key_upper = key_upper[5:].replace('_', '-')
                if key_upper == 'COOKIE':
                    headers[key_upper] = cookie_string
                else:
                    # Some servers don't like when you send the requesting host
                    # through but we do anyway. That's how the nginx reverse
                    # proxy is configured as well.
                    headers[key_upper] = value
            elif key_upper in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                headers[key.replace('_', '-')] = value

        site = RequestSite(request)
        if not 'HOST' in headers:
            headers.update({'HOST': site.domain})
        if not 'X-FORWARDED-FOR' in headers:
            headers.update({'X-FORWARDED-FOR': site.domain})
        if not 'X-REAL-IP' in headers:
            headers.update({'X-REAL-IP': request.META.get('REMOTE_ADDR', None)})
        if not 'COOKIE' in headers:
            headers.update({'COOKIE': cookie_string})

        if request.META.get(
                'CONTENT_TYPE', '').startswith('multipart/form-data'):
            if request.FILES:
                requests_args['files'] = request.FILES
            data = {}
            for key, val in request.POST.iteritems():
                data.update({key:val})
            requests_args['data'] = data
        else:
            requests_args['data'] = request.body

        params = request.GET.copy()

        # If there's a content-length header from Django, it's probably
        # in all-caps and requests might not notice it, so just remove it.
        for key in headers.keys():
            if key.lower() == 'content-length':
                del headers[key]
            elif key.lower() == 'content-type' and request.META.get(
                'CONTENT_TYPE', '').startswith('multipart/form-data'):
                del headers[key]

        requests_args['headers'] = headers
        requests_args['params'] = params
        return requests_args

    @staticmethod
    def translate_response(response):
        proxy_response = HttpResponse(
            response.content, status=response.status_code)
        if 'set-cookie' in response.headers:
            # Here we have to decode the Set-Cookie ourselves because
            # requests will pack the set-cookie headers under the same key,
            # comma separated, which comma SimpleCookie.load() will append
            # to the path in the Morsel class (ie. Path=/,).
            # This of course results in the browser not sending the cookie
            # back to us later on.
            #pylint: disable=protected-access
            set_cookie_lines \
                = response.raw._original_response.msg.getallmatchingheaders(
                'Set-Cookie')
            set_cookies_cont = ''
            set_cookies = []
            for line in set_cookie_lines:
                # The parsing is complicated by the fact that
                # ``getallmatchingheaders`` will return continuation lines
                # as an entry in the list.
                if line.startswith('Set-Cookie'):
                    if set_cookies_cont:
                        set_cookies += [set_cookies_cont]
                    set_cookies_cont = line[11:].strip()
                else:
                    set_cookies_cont += line.strip()
            if set_cookies_cont:
                set_cookies += [set_cookies_cont]

            intercepted_cookies = SimpleCookie()
            for cookie_text in set_cookies:
                intercepted_cookies.load(cookie_text)
            excluded_cookies = set([
                'sessionid', # XXX hardcoded
            ])
            for key in excluded_cookies:
                if key in intercepted_cookies:
                    del intercepted_cookies[key]
            #pylint: disable=maybe-no-member
            proxy_response.cookies.update(intercepted_cookies)

        excluded_headers = set([
            'set-cookie', # Previously parsed.
            # Hop-by-hop headers
            # ------------------
            # Certain response headers should NOT be just tunneled through.
            # For more info, see:
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.5.1
            'connection', 'keep-alive', 'proxy-authenticate',
            'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
            'upgrade',

            # Although content-encoding is not listed among the hop-by-hop
            # headers, it can cause trouble as well.  Just let the server set
            # the value as it should be.
            'content-encoding',

            # Since the remote server may or may not have sent the content
            # in the same encoding as Django will, let Django worry about
            # what the length should be.
            'content-length',
        ])
        for key, value in response.headers.iteritems():
            if key.lower() in excluded_headers:
                continue
            proxy_response[key] = value
        return proxy_response


class SessionProxyView(SessionProxyMixin, TemplateView):

    pass


class AppDashboardView(AppMixin, UpdateView):
    """
    Update a ``App``'s fields associated to the proxy dashboard
    (i.e. entry point and encryption key).
    """

    model = App
    fields = ('entry_point',)
    template_name = 'rules/app_dashboard.html'

    def get_object(self, queryset=None):
        return self.app

    def get_context_data(self, **kwargs):
        context = super(AppDashboardView, self).get_context_data(**kwargs)
        rules = []
        for rule in settings.DB_RULE_OPERATORS:
            look = re.search(r'%\((\S+)\)s', rule[1])
            if look:
                cls_path = look.group(1)
                cls = get_model(cls_path)
                cls_name = cls_path.split('.')[-1].lower()
                try:
                    queryset = cls.objects.filter(
                        organization=self.account, is_active=True)
                except FieldError:
                    queryset = cls.objects.all()
                for obj in queryset:
                    rules += [
                        ('%d/%s' % (rule[0], json.dumps({cls_name: obj.slug})),
                         rule[1] % {cls_path: obj.title})]
            else:
                rules += [rule]
        context.update({'rules': rules, 'organization': self.account})
        return context
