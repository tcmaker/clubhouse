# Identity and Authorization Settings

import os

# We can change the definition of 'accounts.User', but we can't change the
# following setting without an enormous amount of pain.
AUTH_USER_MODEL='accounts.User'

# We do not allow normal password logins and instead require that members
# sign in through OpenID Connect
AUTHENTICATION_BACKENDS = (
    'dashboard.auth.backends.CognitoAuthenticationBackend',
    # 'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
)

# We currently use AWS Cognito for identity. It's possible to use another
# OpenID Connect provider, but that requires changes to these settings and
# various code changes in the `accounts` app.
COGNITO_USER_POOL_ID=os.environ['COGNITO_USER_POOL_ID']


OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_RP_CLIENT_ID = os.environ['COGNITO_CLIENT_ID']
OIDC_RP_CLIENT_SECRET = os.environ['COGNITO_CLIENT_SECRET']
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ['COGNITO_OIDC_AUTHORIZATION_ENDPOINT']
OIDC_OP_TOKEN_ENDPOINT = os.environ['COGNITO_OIDC_TOKEN_ENDPOINT']
OIDC_OP_USER_ENDPOINT = os.environ['COGNITO_OIDC_USER_ENDPOINT']
OIDC_OP_JWKS_ENDPOINT = "https://cognito-idp.us-east-1.amazonaws.com/%s/.well-known/jwks.json" % COGNITO_USER_POOL_ID

# We do not let people self-register for the dashboard, so there is no reason
# to enable this setting.
OIDC_CREATE_USER = False
OIDC_USE_NONCE=False # We should use this, but turning it off eliminates bizarre login errors
OIDC_TOKEN_USE_BASIC_AUTH=True # WARNING: Cognito broke when I disabled this, and I don't know why.

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'https://sso.tcmaker.org/logout?client_id=%s&logout_uri=https://tcmaker.org/' % os.environ['COGNITO_CLIENT_ID']
LOGIN_URL='/accounts/login/'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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
