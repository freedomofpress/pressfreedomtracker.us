"""
Django settings for press freedom tracker project.

Generated by 'django-admin startproject' using Django 1.10.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

from __future__ import absolute_import, unicode_literals

import sys
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import dj_database_url
import logging
logger = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

DEBUG = False
STYLEGUIDE = False

# Application definition

INSTALLED_APPS = [
    'blog',
    'common',
    'forms',
    'incident',
    'statistics',
    'menus',
    'styleguide',
    'dashboard',
    'home',
    'emails',
    'geonames',

    'cloudflare',  # Only really needs to be registered for the test runner
    'build',  # App for static output

    'captcha',
    'wagtailcaptcha',

    'wagtail.contrib.settings',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    # See https://docs.wagtail.io/en/stable/reference/contrib/legacy_richtext.html#legacy-richtext
    'wagtail.contrib.legacy.richtext',
    'wagtail.core',

    'modelcluster',
    'taggit',
    'typogrify',
    'wagtailmetadata',
    'webpack_loader',
    'wagtailautocomplete',
    'wagtailinventory',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

# Must be directly after SecurityMiddleware
if os.environ.get('DJANGO_WHITENOISE'):
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

MIDDLEWARE.extend([
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    # Middleware for content security policy
    'csp.middleware.CSPMiddleware',
])


# Django HTTP settings

# X-XSS-Protection
SECURE_BROWSER_XSS_FILTER = True

# X-Content-Type-Options
SECURE_CONTENT_TYPE_NOSNIFF = True

# We may want to set SECURE_PROXY_SSL_HEADER here


# Make the deployment's onion service name available to templates
ONION_HOSTNAME = os.environ.get('DJANGO_ONION_HOSTNAME')


ROOT_URLCONF = 'tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
                'wagtail.contrib.settings.context_processors.settings',
            ],
            'builtins': ['statistics.templatetags.statistics_tags'],
        },
    },
]

WSGI_APPLICATION = 'tracker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# Set the url as DATABASE_URL in the environment
DATABASES = {
    'default': dj_database_url.config(default="sqlite:///db.sqlite3")
}


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Search Backend

if 'postgres' in DATABASES['default']['ENGINE']:
    INSTALLED_APPS.append('wagtail.contrib.postgres_search')
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.contrib.postgres_search.backend',
        },
    }
else:
    WAGTAILSEARCH_BACKENDS = {}


# Wagtail settings

WAGTAIL_SITE_NAME = "tracker"

WAGTAILIMAGES_IMAGE_MODEL = 'common.CustomImage'


# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'https://pressfreedomtracker.us'


# Django-webpack configuration
WEBPACK_LOADER = {  # noqa: W605
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'bundles/',  # must end with slash
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

# Disable analytics by default
ANALYTICS_ENABLED = False

# Export analytics settings for use in site templates
SETTINGS_EXPORT = [
    'ANALYTICS_ENABLED',
]
# Prevent template variable name collision with wagtail settings
SETTINGS_EXPORT_VARIABLE_NAME = 'django_settings'


RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
NOCAPTCHA = True

# django-taggit
TAGGIT_CASE_INSENSITIVE = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://analytics.freedom.press",
    "https://www.google.com/recaptcha/",
    "https://www.gstatic.com/recaptcha/",
    # For Wagtail Admin
    "'unsafe-inline'",
    # For Twitter Widgets
    "'unsafe-eval'",
    "https://platform.twitter.com",
    # Observable Notebooks
    "https://cdn.jsdelivr.net",
    "https://api.observablehq.com",
    "https://bundle.run",
)
CSP_STYLE_SRC = (
    "'self'",
    # For Wagtail Admin and Twitter Widgets.
    "'unsafe-inline'",
)
CSP_FRAME_SRC = (
    "'self'",
    # For Twitter Widgets
    "https://platform.twitter.com",
    # For recaptcha
    "https://www.google.com/recaptcha/",
    "https://recaptcha.google.com/recaptcha/",
)
CSP_CONNECT_SRC = [
    "'self'",
    "https://analytics.freedom.press",
    # For Wagtail Admin
    "https://releases.wagtail.io/latest.txt",
    # Observable Notebooks
    "https://cdn.jsdelivr.net",
    "https://static.observableusercontent.com/",
]
CSP_IMG_SRC = [
    "'self'",
    "https://analytics.freedom.press",
    # For Twitter Widgets
    "https://platform.twitter.com",
    "https://syndication.twitter.com",
    "https://pbs.twimg.com",
    "https://ton.twimg.com",
    "data:",
]
CSP_OBJECT_SRC = ["'self'"]
CSP_MEDIA_SRC = ["'self'"]

if os.environ.get("DJANGO_CSP_MEDIA_ORIGINS"):
    csp_media_origins = os.environ["DJANGO_CSP_MEDIA_ORIGINS"].split()
    CSP_MEDIA_SRC.extend(csp_media_origins)  # video files
    CSP_IMG_SRC.extend(csp_media_origins)
    CSP_OBJECT_SRC.extend(csp_media_origins)
    CSP_CONNECT_SRC.extend(csp_media_origins)

# Report URI must be a string, not a tuple.
CSP_REPORT_URI = os.environ.get('DJANGO_CSP_REPORT_URI',
                                'https://freedomofpress.report-uri.com/r/d/csp/enforce')

# Logging
#
# Logs are now always JSON. Normally, they go to stdout. To override this for
# development or legacy deploys, set DJANGO_LOG_DIR in the environment.

log_level = os.environ.get("DJANGO_LOG_LEVEL", "info").upper()
log_format = os.environ.get("DJANGO_LOG_FORMAT", "json")
log_stdout = True
log_handler = {
    "formatter": log_format,
    "class": "logging.StreamHandler",
    "stream": sys.stdout,
    "level": log_level,
}

log_dir = os.environ.get("DJANGO_LOG_DIR")
if log_dir:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_stdout = False
    log_handler = {
        "formatter": log_format,
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(log_dir, "django-other.log"),
        "backupCount": 5,
        "maxBytes": 10000000,
        "level": log_level,
    }


TEST_RUNNER = 'common.test_runner.SeededDiscoveryRunner'
RANDOM_SEED = 876394101
