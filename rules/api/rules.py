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

from django.db import transaction
from django.db.models import F, Q, Max
from django.db.utils import IntegrityError
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework import serializers

from .serializers import RuleSerializer
from ..mixins import AppMixin
from ..models import Rule

#pylint: disable=no-init
#pylint: disable=old-style-class


class UpdateRuleSerializer(RuleSerializer):

    class Meta:
        model = Rule
        fields = ('rank', 'path', 'allow', 'is_forward', 'engaged')
        read_only_fields = ('path',)


class RuleMixin(AppMixin):

    model = Rule
    serializer_class = RuleSerializer
    lookup_field = 'path'
    lookup_url_kwarg = 'rule'

    def get_queryset(self):
        return self.model.objects.get_rules(self.app)

    def perform_create(self, serializer):
        # We don't compact ranks after DELETE
        last_rank = self.get_queryset().aggregate(
            Max('rank')).get('rank__max', 0)
        # If the key exists and return None the default value is not applied
        last_rank = last_rank + 1 if last_rank is not None else 1
        serializer.save(app=self.app, rank=last_rank)

    def perform_update(self, serializer):
        serializer.save(app=self.app)


class RuleListAPIView(RuleMixin, ListCreateAPIView):

    def get_queryset(self):
        return super(RuleListAPIView, self).get_queryset().order_by('rank')

    @staticmethod
    def check_path(request):
        if 'path' not in request.data:
            request.data.update({'path': "/"})
        if not request.data['path'].endswith('/'):
            request.data['path'] += '/'
        if not request.data['path'].startswith('/'):
            request.data['path'] = '/' + request.data['path']

    def perform_create(self, serializer):
        try:
            return super(RuleListAPIView, self).perform_create(serializer)
        except IntegrityError as err:
            if 'uniq' in str(err).lower():
                raise serializers.ValidationError({'detail':
                    "Rule with path prefix '%s' already exists."
                    % serializer.validated_data['path']})
            raise

    def post(self, request, *args, **kwargs):
        self.check_path(request)
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Update the rank of rules.

        When receiving a request like [{u'newpos': 1, u'oldpos': 3}],
        it will move the rule at position 3 to position 1, updating all
        rules ranks in-between.
        """
        with transaction.atomic():
            for move in request.data:
                oldpos = move['oldpos']
                newpos = move['newpos']
                queryset = self.get_queryset()
                updated = queryset.get(rank=oldpos)
                if newpos < oldpos:
                    queryset.filter(Q(rank__gte=newpos)
                                    & Q(rank__lt=oldpos)).update(
                        rank=F('rank') + 1, moved=True)
                else:
                    queryset.filter(Q(rank__lte=newpos)
                                    & Q(rank__gt=oldpos)).update(
                        rank=F('rank') - 1, moved=True)
                updated.rank = newpos
                updated.moved = True
                updated.save(update_fields=['rank', 'moved'])
                queryset.filter(moved=True).update(moved=False)
        return self.get(request, *args, **kwargs)


class RuleDetailAPIView(RuleMixin, RetrieveUpdateDestroyAPIView):

    serializer_class = UpdateRuleSerializer
