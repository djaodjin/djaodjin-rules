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

from __future__ import unicode_literals

import logging

from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.authentication import get_authorization_header

from .perms import find_rule
from .utils import get_current_app


LOGGER = logging.getLogger(__name__)


class RulesMiddleware(CsrfViewMiddleware):
    """
    Disables CSRF check if the HTTP request is forwarded.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        view_class = getattr(request.resolver_match.func, 'view_class', None)
        if hasattr(view_class, 'conditional_forward'):
            app = get_current_app(request)
            request.matched_rule, request.matched_params = find_rule(
                request, app)
            if (request.matched_rule and request.matched_rule.is_forward
                and request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE')):
                # We are forwarding the request so the CSRF is delegated
                # to the application handling the forwarded request.
                #pylint:disable=protected-access
                request._dont_enforce_csrf_checks = True
                LOGGER.debug("dont enforce csrf checks on %s %s",
                    request.method, request.path)

        auth = get_authorization_header(request).split()
        if auth and auth[0].lower() in [b'basic', b'bearer']:
            # We need to support API calls from the command line.
            #pylint:disable=protected-access
            request._dont_enforce_csrf_checks = True
            LOGGER.debug("dont enforce csrf checks on %s %s because"\
                " we have an authorization header",
                request.method, request.path)

        return super(RulesMiddleware, self).process_view(
            request, callback, callback_args, callback_kwargs)
