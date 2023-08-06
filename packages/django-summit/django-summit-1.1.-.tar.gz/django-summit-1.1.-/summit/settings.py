# The Summit Scheduler web application
# Copyright (C) 2008 - 2012 Ubuntu Community, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django settings for The Summit Scheduler project.

import os
import sys

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SERVE_STATIC = True

OPENID_STRICT_USERNAMES=True
OPENID_FOLLOW_RENAMES=True

from common import utils
VERSION_STRING = utils.get_summit_version(
                        os.path.join(PROJECT_PATH, "version"),
                        DEBUG)

SITE_ROOT = 'http://summit.ubuntu.com'

ADMINS = (
#    ('Your Name', 'admin@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'summit',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "common.context_processors.next_summit",
    "common.context_processors.login_redirect",
    "common.context_processors.url_base",
    "common.context_processors.summit_version",
    "common.context_processors.site_menu",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'summit.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django_openid_auth',
    'django.contrib.admin',
    'django.contrib.sites',
    'summit.schedule',
    'summit.sponsor',
    'summit.common',
    'south',
]

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Should users be created when new OpenIDs are used to log in?
OPENID_CREATE_USERS = True

# Can we reuse existing users?
OPENID_REUSE_USERS = True

# When logging in again, should we overwrite user details based on
# data received via Simple Registration?
OPENID_UPDATE_DETAILS_FROM_SREG = True

# If set, always use this as the identity URL rather than asking the
# user.  This only makes sense if it is a server URL.
OPENID_SSO_SERVER_URL = 'https://login.launchpad.net/'

# Tell django.contrib.auth to use the OpenID signin URLs.
LOGIN_URL = '/openid/login'
LOGIN_REDIRECT_URL = '/'

LAUNCHPAD_CACHE = os.path.join(PROJECT_PATH, 'lp-cache')

CACHE_BACKEND = 'locmem:///'

# Manage apps from bzr branches
try:
    import bzr_apps
    INSTALLED_APPS.append('bzr_apps')
except:
    pass

BZR_APPS = {
    ## ubuntu-django-foundations app management
    'bzr_apps': ('http://bazaar.launchpad.net/~django-foundations-dev/ubuntu-django-foundations/bzr_apps', '7'),

    ## ubuntu-website supplied templates and styles
    'ubuntu_website': ('http://bazaar.launchpad.net/~ubuntu-community-webthemes/ubuntu-community-webthemes/light-django-theme', '42'),

    ## linaro-website supplied templates and styles
    'linaro_website': ('http://bazaar.launchpad.net/~linaro-infrastructure/ubuntu-community-webthemes/light-django-linaro-theme', '43'),

    ## twidenash supplied microblog embedding javascript
    'media/js/twidenash': ('http://bazaar.launchpad.net/~django-foundations-dev/twidenash/2.0/', '3'),
}

import logging
try:
  from local_settings import *
except ImportError:
  logging.warning("No local_settings.py were found. See INSTALL for instructions.")
