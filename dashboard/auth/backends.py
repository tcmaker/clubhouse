from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from accounts.models import User

class CognitoAuthenticationBackend(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        sub = claims.get('sub')
        if not sub:
            return self.UserModel.objects.none()

        try:
            u = User.objects.get(sub=sub)
        except User.DoesNotExist:
            return self.UserModel.objects.none()

        try:
            u.sync_membership_info()
        except Exception:
            # It would be nice to be able to do this, but the show must go on
            pass

        return [u] # caller expects a list
