from django.db import models
import django.utils.timezone

class ActiveInviteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(expires_at__gt=django.utils.timezone.now())

class PendingApprovalManager(models.Manager):
    """Invitations that are ready for approval"""

    def completed_application(self):
        qs = self.get_queryset()
        return qs.filter(application_completed_at__isnull=False)

    def pending_keyfobs(self):
        return self.completed_application().filter(keyfob_issued_at__isnull=True)

    def pending_approval(self):
        return self.completed_application().filter(
            keyfob_issued_at__isnull=False,
            account_invitation_created_at__isnull=True
        )
