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

import json

from django.utils import six
from rest_framework import serializers

from .. import settings
from ..models import Rule, App

#pylint: disable=no-init
#pylint: disable=old-style-class


class AppSerializer(serializers.ModelSerializer):

    class Meta:
        model = App
        fields = ('slug', 'entry_point', )
        read_only_fields = ('slug',)

    @staticmethod
    def validate_entry_point(value):
        """
        Prevent unsafe URLs
        """
        parts = six.moves.urllib.parse.urlparse(value)
        if (not parts.netloc
            or parts.netloc.startswith('localhost')
            or parts.netloc.startswith('127.0.0.1')):
            raise serializers.ValidationError("Unsafe URLs are not allowed.")
        return value


class RuleSerializer(serializers.ModelSerializer):
    allow = serializers.CharField(required=False, source='get_allow')
    is_forward = serializers.BooleanField(required=False)

    class Meta:
        model = Rule
        fields = ('rank', 'path', 'allow', 'is_forward', )

    def validate(self, attrs):
        #pylint: disable=super-on-old-class
        if 'get_allow' in attrs:
            parts = attrs.get('get_allow').split('/')
            try:
                rule_op = int(parts[0])
                if rule_op < 0 or rule_op >= len(settings.DB_RULE_OPERATORS):
                    raise ValueError("unknown rule %d" % rule_op)
                if len(parts) > 1:
                    params = json.loads(parts[1])
                    kwargs = {}
                    for key, dft in six.iteritems(
                            settings.RULE_OPERATORS[rule_op][2]):
                        if key in params:
                            kwargs[key] = params[key]
                        else:
                            kwargs[key] = dft
                    kwargs_encoded = json.dumps(kwargs)
                else:
                    kwargs_encoded = ""
                attrs['rule_op'] = rule_op
                attrs['kwargs'] = kwargs_encoded
            except ValueError as err:
                raise serializers.ValidationError(str(err))
        return super(RuleSerializer, self).validate(attrs)


class UsernameSerializer(serializers.Serializer):

    username = serializers.SerializerMethodField()

    class Meta:
        fields = ('username',)
        read_only_fields = ('username',)

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    @staticmethod
    def get_username(request):
        return request.user.username
