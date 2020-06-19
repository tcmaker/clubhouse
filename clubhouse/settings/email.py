DEFAULT_FROM_EMAIL = 'membership@tcmaker.org'

# TODO: use mailcatcher or an equivalent as a default in development environments
EMAIL_BACKEND='django_ses.SESBackend'

SERVER_EMAIL='stephen.vandahm@tcmaker.org'
ADMINS = [('stephen.vandahm@tcmaker.org', 'stephen.vandahm@tcmaker.org')]
MANAGERS = ADMINS
