from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import redirect

import .rest_actions

from django.contrib.auth.mixins import AccessMixin

class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class ActiveMembershipRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and has an active membership."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user_is_authenticated:
            return self.handle_no_permission()

        record = request.user.get_member_record()
        if not record:
            return self.handle_no_permission()

        if not request.user.has_active_membership():
            return redirect('/dashboard/activate')

        return super().dispatch(request, *args, **kwargs)
