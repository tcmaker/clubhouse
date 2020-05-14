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
