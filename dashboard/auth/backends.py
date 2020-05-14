from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from ..models import User

class CognitoAuthenticationBackend(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        sub = claims.get('sub')
        if not sub:
            return self.UserModel.objects.none()

        try:
            return User.objects.get(sub=sub)

        except User.DoesNotExist:
            return self.UserModel.objects.none()

    def get_token(self, payload):
        """Return token object as a dictionary."""

        auth = None
        if self.get_settings('OIDC_TOKEN_USE_BASIC_AUTH', False):
            # When Basic auth is defined, create the Auth Header and remove secret from payload.
            user = payload.get('client_id')
            pw = payload.get('client_secret')

            print(payload.__dict__)

            auth = HTTPBasicAuth(user, pw)
            del payload['client_secret']

        response = requests.post(
            self.OIDC_OP_TOKEN_ENDPOINT,
            data=payload,
            auth=auth,
            verify=self.get_settings('OIDC_VERIFY_SSL', True))

        response.raise_for_status()
        return response.json()
