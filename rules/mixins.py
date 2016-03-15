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

import logging

from . import settings
from .models import Engagement
from .utils import datetime_or_now
from .extras import AppMixinBase


LOGGER = logging.getLogger(__name__)


class AppMixin(AppMixinBase, settings.EXTRA_MIXIN):
    pass


class EngagementMixin(object):
    """
    Records ``Engagement`` with a ``App``.
    """
    engagement_trigger = 'default'

    @property
    def last_visited(self):
        if not hasattr(self, '_last_visited'):
            self._last_visited = None
            if self.request.user.is_authenticated():
                engagement, created = Engagement.objects.get_or_create(
                    slug=self.engagement_trigger, user=self.request.user)
                if created:
                    # Avoid too many INSERT statements
                    engagement.last_visited = datetime_or_now()
                    engagement.save()
                    LOGGER.info("initial '%s' engagement with %s",
                        self.engagement_trigger, self.request.path)
                else:
                    self._last_visited = engagement.last_visited
        return self._last_visited

    def get_context_data(self, **kwargs):
        context = super(EngagementMixin, self).get_context_data(**kwargs)
        context.update({'last_visited': self.last_visited})
        return context
