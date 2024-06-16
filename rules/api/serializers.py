# Copyright (c) 2024, DjaoDjin inc.
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

import json

from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from rest_framework import serializers

from .. import settings
from ..compat import gettext_lazy as _, six
from ..models import Rule
from ..utils import get_app_model


class EnumField(serializers.ChoiceField):
    """
    Treat a ``PositiveSmallIntegerField`` as an enum.
    """
    translated_choices = {}

    def __init__(self, choices, *args, **kwargs):
        self.translated_choices = {key: slugify(val) for key, val in choices}
        super(EnumField, self).__init__([(slugify(val), key)
            for key, val in choices],
            *args, **kwargs)

    def to_representation(self, value):
        if isinstance(value, list):
            result = [slugify(self.translated_choices.get(item, None))
                for item in value]
        else:
            result = slugify(self.translated_choices.get(value, None))
        return result

    def to_internal_value(self, data):
        if isinstance(data, list):
            result = [self.choices.get(item, None) for item in data]
        else:
            result = self.choices.get(data, None)
        if result is None:
            if not data:
                raise serializers.ValidationError(
                    _("This field cannot be blank."))
            raise serializers.ValidationError(
                _("'%(data)s' is not a valid choice."\
                " Expected one of %(choices)s.") % {
                    'data': data, 'choices': [str(choice)
                    for choice in six.iterkeys(self.choices)]})
        return result


class NoModelSerializer(serializers.Serializer):

    def create(self, validated_data):
        raise RuntimeError('`create()` should not be called.')

    def update(self, instance, validated_data):
        raise RuntimeError('`update()` should not be called.')


class AppSerializer(serializers.ModelSerializer):

    authentication = EnumField(
        choices=get_app_model().AUTH_TYPE, required=False,
        help_text=_("Restricted authentication and registration"))

    detail = serializers.CharField(required=False,
        help_text=_("Describes the result of the action"\
            " in human-readable form"))

    class Meta:
        model = get_app_model()
        fields = ('slug', 'entry_point', 'session_backend', 'authentication',
            'welcome_email', 'cors_restricted', 'detail')
        read_only_fields = ('slug', 'detail')

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


class AppKeySerializer(serializers.ModelSerializer):
    """
    Used when a secret key is generated.
    """
    enc_key = serializers.CharField(read_only=True,
        help_text=_("Key used to decrypt the encoded session information."))

    class Meta:
        model = get_app_model()
        fields = ('enc_key',)


class RuleSerializer(serializers.ModelSerializer):

    allow = serializers.CharField(required=False, source='get_allow',
        help_text=_("Method applied to grant or deny access"))
    is_forward = serializers.BooleanField(required=False,
        help_text=_("When access is granted, should the request be forwarded"))
    engaged = serializers.CharField(required=False, allow_blank=True,
        help_text=_("Tags to check if it is the first time a user engages"))

    class Meta:
        model = Rule
        fields = ('rank', 'path', 'allow', 'is_forward', 'engaged')

    def validate(self, attrs):
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
            del attrs['get_allow']
        return super(RuleSerializer, self).validate(attrs)


class RuleRankSerializer(NoModelSerializer):

    oldpos = serializers.IntegerField(
        help_text=_("old rank for a rule in the list of rules"))
    newpos = serializers.IntegerField(
        help_text=_("new rank for the rule in the list of rules"))


class RuleRankUpdateSerializer(NoModelSerializer):

    updates = RuleRankSerializer(many=True)


class SessionDataSerializer(NoModelSerializer):

    forward_session = serializers.CharField(
        help_text=_("The session being forwarded"))
    forward_session_header = serializers.CharField(
        help_text=_("The HTTP header that encodes the session"))
    forward_url = serializers.CharField(
        help_text=_("The URL end point where the request is forwarded"))

    class Meta:
        fields = ('forward_session', 'forward_session_header', 'forward_url')
        read_only_fields = ('forward_session', 'forward_session_header',
            'forward_url')


class UsernameSerializer(NoModelSerializer):

    username = serializers.SerializerMethodField()

    class Meta:
        fields = ('username',)
        read_only_fields = ('username',)

    @staticmethod
    def get_username(request):
        return request.user.username


class UserEngagementSerializer(serializers.ModelSerializer):

    # Implementation Note:
    #   This serializer is used in a GET request but it will run
    #   a `rest_framework.UniqueValidator` if left unchecked when
    #   we run `_validate_examples` in the API doc generator.
    username = serializers.CharField(help_text=_("Username"))
    engagements = serializers.SerializerMethodField(
        help_text=_("Engagement tags for username"))

    class Meta:
        model = get_user_model()
        fields = ('username', 'engagements')

    @staticmethod
    def get_engagements(obj):
        engs = obj.engagements.all()
        user_tags = []
        for eng in engs:
            if eng.slug and not eng.slug.isspace():
                user_tags.append(eng.slug.strip())
        return list(set(user_tags))


class EngagementSerializer(NoModelSerializer):

    slug = serializers.CharField(
        help_text=_("Engagement tag"))
    count = serializers.IntegerField(
        help_text=_("Number of users that have engaged with this tag"))


class EngagementsSerializer(NoModelSerializer):

    engagements = EngagementSerializer(many=True,
        help_text=_("Engagement tags by user"))
    active_users = serializers.IntegerField(
        help_text=_("Number of users that have engaged with the app"))
    authentication = EnumField(
        choices=get_app_model().AUTH_TYPE, required=False,
        help_text=_("Restricted authentication and registration"))


class ValidationErrorSerializer(NoModelSerializer):
    """
    Details on why token is invalid.
    """
    detail = serializers.CharField(help_text=_("Describes the reason for"\
        " the error in plain text"))
