# Integrations with External services.
#
# A few notes:
#
#     1. SSO integrations are in `identity.py`
#     2. AWS client libraries can get credentials from environment variables,
#        a shared credentials file, or from the AWS role the app is deployed
#        under. We do not need to pass them in as settings and should not
#        do so.

import os

BILLING_SYSTEM_API_URL=os.environ.get('BILLING_SYSTEM_API_URL')
BILLING_SYSTEM_API_TOKEN=os.environ.get('BILLING_SYSTEM_API_TOKEN')

#### CiviCRM ####
CIVICRM_URL_BASE = os.environ.get('CIVICRM_URL_BASE')
CIVICRM_API_KEY = os.environ.get('CIVICRM_API_KEY')
CIVICRM_SITE_KEY = os.environ.get('CIVICRM_SITE_KEY')
CIVICRM_API_URL_BASE = os.environ.get('CIVICRM_API_URL_BASE')

# CiviCRM custom fields include primary keys and vary across installations,
# even if you name them the same
CIVICRM_FIELD_EMERGENCY_CONTACT_NAME = os.environ.get('CIVICRM_FIELD_EMERGENCY_CONTACT_NAME')
CIVICRM_FIELD_EMERGENCY_CONTACT_PHONE = os.environ.get('CIVICRM_FIELD_EMERGENCY_CONTACT_PHONE')
CIVICRM_FIELD_ACCEPTED_LIABILITY_WAIVER = os.environ.get('CIVICRM_FIELD_ACCEPTED_LIABILITY_WAIVER')

#### SQS for Timeslots ####
TIMESLOT_QUEUE_URL = os.environ['TIMESLOT_QUEUE_URL']

#### File storage ####
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'tcmaker-clubhouse-uploads-prod'

#### Payment ####
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PRODUCT_ONE_MONTH_PLAN=os.environ.get('STRIPE_PRODUCT_ONE_MONTH_PLAN')
STRIPE_PRODUCT_SIX_MONTH_PLAN=os.environ.get('STRIPE_PRODUCT_SIX_MONTH_PLAN')
STRIPE_PRODUCT_TWELVE_MONTH_PLAN=os.environ.get('STRIPE_PRODUCT_TWELVE_MONTH_PLAN')
