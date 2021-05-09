import os

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = False # In our use case, this causes more problems than it solves.

ROOT_URLCONF = 'clubhouse.urls'
WSGI_APPLICATION = 'clubhouse.wsgi.application'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=False
if 'ENVIRONMENT' in os.environ and os.environ['ENVIRONMENT'] == 'development':
    DEBUG = True

# Sometimes the app needs to be able to refer to its own fully-qualified URL
# or hostname. By itself, it has no way to figure this out, so we help it along.

__server_host_url = os.environ['SERVER_PROTOCOL'] + '://' + os.environ['SERVER_HOSTNAME']
if 'SERVER_PORT' in os.environ:
    __server_host_url += ':' + os.environ['SERVER_PORT']

WEBAPP_URL_BASE=__server_host_url

# This allows the application to work with an Elastic Load Balancer, or behind
# the AWS API Gateway with Zappa
ALLOWED_HOSTS = [
    os.environ['SERVER_HOSTNAME']
]

# This header is how the load balancer lets us know we're running in HTTPS and
# that it has decoded the HTTPS for us.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Libraries
    'compressor',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_bootstrap_breadcrumbs',
    'django_extensions',
    'sslserver', # self-signed ssl dev server for testing with cognito
    'localflavor',
    'mozilla_django_oidc',
    'phonenumber_field',
    'tempus_dominus',

    # Mine
    'accounts.apps.AccountsConfig',
    'approvals.apps.ApprovalsConfig',
    'consumables.apps.ConsumablesConfig',
    'dashboard.apps.DashboardConfig',
    'landing.apps.LandingConfig',
    'member_profile.apps.MemberProfileConfig',
    'renew.apps.RenewConfig',
    'signup.apps.SignupConfig',
    'storage.apps.StorageConfig',
    'timeslots.apps.TimeslotsConfig',
    'workshop.apps.WorkshopConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.auth.MembershipStatusMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
]

# Content Security Policy (django-csp)
CSP_DEFAULT_SRC = (
    "'self'",
    "data:",
    "'unsafe-inline'",
    'fonts.googleapis.com',
    'js.stripe.com',
    'fonts.gstatic.com',
    'tcmaker-clubhouse-uploads-prod.s3.amazonaws.com',
)

CSP_CONNECT_SRC = ("'self'", 'api.stripe.com',)
CSP_FRAME_SRC = ('js.stripe.com', 'hooks.stripe.com')
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    'cdnjs.cloudflare.com',
    'code.jquery.com',
    'js.stripe.com',
    'stackpath.bootstrapcdn.com',
    'cdn.jsdelivr.net',
    'cdnjs.cloudflare.com',
)

CSP_STYLE_SRC = (
    "'self'",
    'cdnjs.cloudflare.com',
    'fonts.googleapis.com',
    "'unsafe-inline'",
)

CSP_FONT_SRC = (
    "'self'",
    "data:",
    'fonts.googleapis.com',
    'fonts.gstatic.com',
)

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

DEFAULT_AUTO_FIELD='django.db.models.AutoField'
