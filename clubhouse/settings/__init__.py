"""
Django settings for clubhouse project.

Many high-functioning Django projects divide this folder into separate files
for each environment. We run Clubhouse in the style of a 12-factor app, so
we pass anything that changes between environments into the app through
environment variables.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from clubhouse.settings.core import *
from clubhouse.settings.email import *
from clubhouse.settings.identity import *
from clubhouse.settings.integrations import *
from clubhouse.settings.ui import *

#### 12-Factor App Settings (Heroku, etc) ####
import django_heroku
django_heroku.settings(locals())

# Hack to get PostgreSQL to work on localhost
if os.environ['SERVER_HOSTNAME'] == 'localhost':
    del DATABASES['default']['OPTIONS']['sslmode']

# Test Database
DATABASES['default']['TEST'] = {
    'NAME': 'django-clubhouse-test'
}
