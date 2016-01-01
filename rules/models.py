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

"""
Models for the rules application.
"""

import datetime, logging

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from django.db import models
from django.utils.timezone import utc
from django.utils.module_loading import import_string

from . import settings


LOGGER = logging.getLogger(__name__)


class Engagement(models.Model):
    """
    This model tracks engagement of a user with the website in order
    to answer questions such as:
        - Has a user either edited a page?
    """
    slug = models.SlugField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='engagements')
    last_visited = models.DateTimeField(
        default=datetime.datetime(1971, 1, 1).replace(tzinfo=utc))
    # 1971 instead of 1970 to avoid Overflow exception in South.

    class Meta:
        unique_together = ('slug', 'user')

    def __unicode__(self):
        return '%s-%s' % (self.slug, unicode(self.user))


class AppManager(models.Manager):

    def get_or_create(self, defaults=None, **kwargs):
        app, created = super(AppManager, self).get_or_create(
            defaults=defaults, **kwargs)
        for rank_min_one, (path, rule_op, is_forward) \
            in enumerate([('/', Rule.ANY, False)]):
            #pylint:disable=no-member
            Rule.objects.db_manager(using=self._db).get_or_create(
                app=app, rank=rank_min_one + 1,
                path=path, rule_op=rule_op, is_forward=is_forward)
        return app, created


class BaseApp(models.Model): #pylint: disable=super-on-old-class
    """
    A ``App`` is used to select a database and a firewall profile.

    Implementation Note:
    Because we use separate databases, ``App`` and ``Organization``
    have no direct relationship (inheritance, foreign key, etc.).
    The same ``slug`` will though indistincly pickup a ``App`` and/or
    the matching ``Organization``.
    """

    # Most DNS provider limit subdomain length to 25 characters.
    # XXX need to find actual regular expression.
    slug = models.SlugField(max_length=25, unique=True,
        help_text="unique subdomain of root site")

    account = models.ForeignKey(settings.ACCOUNT_MODEL, null=True)

    # Fields for proxy features
    entry_point = models.URLField(max_length=100,
       help_text='Entry point to which requests will be redirected to')
    enc_key = models.TextField(max_length=480, verbose_name='Encryption Key',
       help_text='Encryption key used to sign proxyed requests')
    forward_session = models.BooleanField(default=True)

    def __unicode__(self): #pylint: disable=super-on-old-class
        return unicode(self.slug)

    def printable_name(self): # XXX Organization full_name
        return unicode(self)

    def get_rules(self):
        return Rule.objects.db_manager(using=self._state.db).filter(
            app=self).order_by('rank')

    objects = AppManager()

    class Meta:
        swappable = 'RULES_APP_MODEL'
        abstract = True


class App(BaseApp):

    def __unicode__(self): #pylint: disable=super-on-old-class
        return unicode(self.slug)


class Rule(models.Model):
    """
    Rule to check in order to forward request, serve it locally
    and editing the content coming back through the proxy.
    """
    #pylint: disable=old-style-class,no-init

    HOME = 'index'
    ANY = 0

    app = models.ForeignKey(settings.RULES_APP_MODEL)
    # XXX At first I wanted to use a URLField for validation but this only
    #     works for URLs starting with a http/ftp protocol. What we really
    #     want here is a Path validator (including /).
    path = models.CharField(max_length=255)
    rule_op = models.PositiveSmallIntegerField(
        choices=settings.DB_RULE_OPERATORS, default=ANY)
    kwargs = models.CharField(max_length=255, default="")
    is_forward = models.BooleanField(default=True)
    rank = models.IntegerField()
    moved = models.BooleanField(default=False)

    class Meta:
        unique_together = (('app', 'rank', 'moved'), ('app', 'path'))

    def __unicode__(self):
        return unicode('%s/%s' % (self.app, self.path))

    def get_allow(self):
        if self.kwargs:
            return '%d/%s' % (self.rule_op, self.kwargs)
        return '%d' % self.rule_op


def get_app_model():
    """
    Returns the Site model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.RULES_APP_MODEL)
    except ValueError:
        raise ImproperlyConfigured(
            "RULES_APP_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured("RULES_APP_MODEL refers to model '%s'"\
" that has not been installed" % settings.RULES_APP_MODEL)


def get_current_app():
    """
    Returns the default app for a site.
    """
    if settings.DEFAULT_APP_CALLABLE:
        app = import_string(settings.DEFAULT_APP_CALLABLE)()
        LOGGER.debug("rules.get_current_app: '%s'", app)
    else:
        app = get_app_model().get(pk=settings.DEFAULT_APP_ID)
    return app

