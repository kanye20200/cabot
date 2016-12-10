from .base import *

import os

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GoogleOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP = os.environ.get('AUTH_LDAP', 'false')

if AUTH_LDAP.lower() == "true":
    from settings_ldap import *
    AUTHENTICATION_BACKENDS += tuple(['django_auth_ldap.backend.LDAPBackend'])


_TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GoogleOAuth',
)

SOCIAL_AUTH_USER_MODEL = 'auth.User'
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_RAISE_EXCEPTIONS = True
RAISE_EXCEPTIONS = True

SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = os.environ.get('OAUTH2_WHITELISTED_DOMAINS', 'example.com').split(',')
GOOGLE_OAUTH2_SOCIAL_AUTH_RAISE_EXCEPTIONS = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET')
COMPRESS_ENABLED = False
LOGIN_REDIRECT_URL = '/'

# Use cloudwatch to monitor cabot alerts
AWS_CLOUDWATCH_SYNC = os.environ.get('AWS_CLOUDWATCH_SYNC', False)
AWS_CLOUDWATCH_REGION = os.environ.get('AWS_CLOUDWATCH_REGION', 'us-east-1')
AWS_CLOUDWATCH_ACCESS_KEY = os.environ.get('AWS_CLOUDWATCH_ACCESS_KEY', None)
AWS_CLOUDWATCH_SECRET_KEY = os.environ.get('AWS_CLOUDWATCH_SECRET_KEY', None)
AWS_CLOUDWATCH_PREFIX = os.environ.get('AWS_CLOUDWATCH_PREFIX', None)
AWS_CLOUDWATCH_NAMESPACE = os.environ.get('AWS_CLOUDWATCH_NAMESPACE', 'Cabot')
