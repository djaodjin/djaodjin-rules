# Copyright (c) 2019, DjaoDjin inc.
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

from random import choice

from rest_framework.response import Response
from rest_framework.generics import (UpdateAPIView,
    RetrieveUpdateAPIView)

from ..mixins import AppMixin
from ..utils import get_app_model
from .serializers import AppSerializer, AppKeySerializer

#pylint: disable=no-init
#pylint: disable=old-style-class


class GenerateKeyAPIView(AppMixin, UpdateAPIView):
    """
    Rotates session encoding key

    Rotates the key used to encode the session information forwarded
    to the application entry point.

    **Tags: rbac

    **Examples

    .. code-block:: http

        PUT /api/proxy/key/ HTTP/1.1

    responds

    .. code-block:: json

        {
          "enc_key": "********"
        }
    """
    # XXX change to POST
    model = get_app_model()
    serializer_class = AppKeySerializer

    def update(self, request, *args, **kwargs):
        self.object = self.app
        self.object.enc_key = "".join([
                choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^*-_=+")
                for idx in range(16)]) #pylint: disable=unused-variable
        self.object.save()
        return Response(AppKeySerializer().to_representation(self.object))


class AppUpdateAPIView(AppMixin, RetrieveUpdateAPIView):
    """
    Returns the URL endpoint to which requests passing the access rules
    are forwarded to, and the format in which the session information
    is encoded.

    When running tests, you can retrieve the actual session information
    for a specific user through the `/proxy/sessions/{user}/` API call.

    **Tags: rbac

    **Examples

    .. code-block:: http

        GET /api/proxy/ HTTP/1.1

    responds

    .. code-block:: json

        {
          "slug": "cowork",
          "entry_point": "http://localhost:8001/",
          "session_backend": 1
        }
    """
    model = get_app_model()
    serializer_class = AppSerializer

    def get_object(self):
        return self.app

    def put(self, request, *args, **kwargs):
        """
        Updates forward end-point

        Updates the URL endpoint to which requests passing the access rules
        are forwarded to and/or the format in which the session information
        is encoded.

        **Tags: rbac

        **Examples

        .. code-block:: http

            PUT /api/proxy/ HTTP/1.1

        .. code-block:: json

            {
              "entry_point": "http://localhost:8001/",
              "session_backend": 1
            }

        responds

        .. code-block:: json

            {
              "slug": "cowork",
              "entry_point": "http://localhost:8001/",
              "session_backend": 1
            }
        """
        return super(AppUpdateAPIView, self).put(request, *args, **kwargs)
