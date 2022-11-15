# Django settings for testsite project.

import logging, os, re, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_DIR = os.getcwd()

#JS_FRAMEWORK = 'angularjs'
JS_FRAMEWORK = 'vuejs'

def load_config(confpath):
    '''
    Given a path to a file, parse its lines in ini-like format, and then
    set them in the current namespace.
    '''
    # todo: consider using something like ConfigObj for this:
    # http://www.voidspace.org.uk/python/configobj.html
    if os.path.isfile(confpath):
        sys.stderr.write('config loaded from %s\n' % confpath)
        with open(confpath) as conffile:
            line = conffile.readline()
            while line != '':
                if not line.startswith('#'):
                    look = re.match(r'(\w+)\s*=\s*(.*)', line)
                    if look:
                        value = look.group(2) \
                            % {'LOCALSTATEDIR': BASE_DIR + '/var'}
                        # Once Django 1.5 introduced ALLOWED_HOSTS (a tuple
                        # definitely in the site.conf set), we had no choice
                        # other than using eval. The {} are here to restrict
                        # the globals and locals context eval has access to.
                        # pylint: disable=eval-used
                        setattr(sys.modules[__name__],
                            look.group(1).upper(), eval(value, {}, {}))
                line = conffile.readline()
    else:
        sys.stderr.write('warning: config file %s does not exist.\n' % confpath)

load_config(os.path.join(
    os.getenv('TESTSITE_SETTINGS_LOCATION', RUN_DIR), 'credentials'))

DEBUG = True
FEATURES_DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'testsite.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'testsite.wsgi.application'

INSTALLED_APPS = (
    'django_extensions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'rest_framework',
    'deployutils.apps.django',
    'rules',
    'testsite'
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '/static/vendor/jquery.js',
    'SHOW_COLLAPSED': True,
    'SHOW_TEMPLATE_CONTEXT': True,
}

INTERNAL_IPS = ('127.0.0.1', '::1')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(RUN_DIR, 'db.sqlite'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

REST_FRAMEWORK = {
    'PAGE_SIZE': 25,
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MIDDLEWARE = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
)

MIDDLEWARE_CLASSES = MIDDLEWARE

# Templates (Django 1.8+)
# ----------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'testsite', 'templates'),
                 os.path.join(BASE_DIR, 'rules', 'templates')),
        'OPTIONS': {
            'context_processors': [
    'django.contrib.auth.context_processors.auth', # because of admin/
    'django.contrib.messages.context_processors.messages', # because of admin/
    'django.template.context_processors.request',
    'django.template.context_processors.media',
    'testsite.context_processors.js_framework'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'],
            'libraries': {},
            'builtins': [
                'deployutils.apps.django.templatetags.deployutils_prefixtags',
                'deployutils.apps.django.templatetags.deployutils_extratags'
            ]
        }
    }
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/proxy/rules/'

# Allow user to enter month in durationfield
DURATIONFIELD_ALLOW_MONTHS = True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'logfile':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'rules': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}
if logging.getLogger('gunicorn.error').handlers:
    LOGGING['handlers']['logfile'].update({
        'class':'logging.handlers.WatchedFileHandler',
        'filename': os.path.join(RUN_DIR, 'testsite-app.log')
    })


# Session settings
# ----------------
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Rules application
# -----------------
RULES = {
    'RULE_OPERATORS': (
        '',                                            # 0
        'rules.settings.fail_authenticated',           # 1
        'testsite.decorators.fail_direct',             # 2
    ),
}
