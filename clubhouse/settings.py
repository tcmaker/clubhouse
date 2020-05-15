"""
Django settings for clubhouse project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.contrib.messages import constants as messages

# Overrides to make messages framework work with Bootstrap classes
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=True
if 'ENVIRONMENT' in os.environ and os.environ['ENVIRONMENT'] != 'development':
    DEBUG = False

__server_host_url = os.environ['SERVER_PROTOCOL'] + '://' + os.environ['SERVER_HOSTNAME']
if 'SERVER_PORT' in os.environ:
    __server_host_url += ':' + os.environ['SERVER_PORT']

ALLOWED_HOSTS = [
    os.environ['SERVER_HOSTNAME']
]

WEBAPP_URL_BASE=__server_host_url

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.admindocs',

    # Libraries
    'django_extensions',
    'phonenumber_field',
    'localflavor',
    'crispy_forms',
    'django_bootstrap_breadcrumbs',
    'mozilla_django_oidc',

    # Mine
    # 'signup.apps.SignupConfig',
    'dashboard.apps.DashboardConfig',
    # 'kiosk.apps.KioskConfig',
    # 'approvals.apps.ApprovalsConfig',
    # 'storage.apps.StorageConfig',
    # 'endorsements.apps.EndorsementsConfig',
    'timeslots.apps.TimeslotsConfig',
    'workshop.apps.WorkshopConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'mozilla_django_oidc.middleware.SessionRefresh',
]

ROOT_URLCONF = 'clubhouse.urls'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'clubhouse.wsgi.application'

AUTH_USER_MODEL='dashboard.User'
# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTHENTICATION_BACKENDS = (
    'dashboard.auth.backends.CognitoAuthenticationBackend',
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

OIDC_RP_SIGN_ALGO = 'RS256'
# OIDC_RP_IDP_SIGN_KEY = 'RS256'
OIDC_OP_JWKS_ENDPOINT = os.environ['COGNITO_OIDC_JWKS_ENDPOINT']
OIDC_RP_CLIENT_ID = os.environ['COGNITO_CLIENT_ID']
OIDC_RP_CLIENT_SECRET = os.environ['COGNITO_CLIENT_SECRET']
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ['COGNITO_OIDC_AUTHORIZATION_ENDPOINT']
OIDC_OP_TOKEN_ENDPOINT = os.environ['COGNITO_OIDC_TOKEN_ENDPOINT']
OIDC_OP_USER_ENDPOINT = os.environ['COGNITO_OIDC_USER_ENDPOINT']
OIDC_CREATE_USER = False
OIDC_USE_NONCE=True
OIDC_TOKEN_USE_BASIC_AUTH=True
# OIDC_AUTHENTICATION_CALLBACK_URL='https://clubhouse.tcmaker.org/oidc/callback/'

COGNITO_USER_POOL_ID=os.environ['COGNITO_USER_POOL_ID']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = 'https://tcmaker.org/'
LOGOUT_REDIRECT_URL = 'https://sso.tcmaker.org/logout?client_id=%s&logout_uri=https://tcmaker.org/' % os.environ['COGNITO_CLIENT_ID']
LOGIN_URL='/dashboard/login/'


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = False # In our use case, this causes more problems than it solves.

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']

SERVER_EMAIL='stephen.vandahm@tcmaker.org'
MANAGERS = os.environ['MANAGER_EMAILS'].split(',')
# get rid of trailing '' if there's only one manager
if len(MANAGERS) > 1 and MANAGERS[-1] == '':
    MANAGERS.pop()

ADMINS = MANAGERS

#### Heroku ####
import django_heroku
django_heroku.settings(locals())

# Hack to get PostgreSQL to work on localhost
if os.environ['SERVER_HOSTNAME'] == 'localhost':
    del DATABASES['default']['OPTIONS']['sslmode']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
