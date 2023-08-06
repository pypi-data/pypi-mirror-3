# -*- coding: utf-8 -*-
import os, settings

PATH = os.path.dirname(__file__)

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = settings.STATIC_ROOT

# Local settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PATH, 'dev.db'),   # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = settings.INSTALLED_APPS + (
    'debug_toolbar',
	'django_evolution',
)

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend' #'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_PORT = 25

DEFAULT_FROM_EMAIL = 'Site Name <site-name-noreply@site-domain.com>'
EMAIL_SUBJECT_PREFIX = '[Site Name] '

FACEBOOK_APP_ID              = ''
FACEBOOK_API_SECRET          = ''

# Settings for Django Debug Toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#    'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
#    'TAG': 'div',
}
