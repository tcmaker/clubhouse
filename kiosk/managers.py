from django.db import models
import django.utils.timezone

class ActiveInviteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(expires_at__gt=django.utils.timezone.now())

class PendingApprovalManager(models.Manager):
    """Invitations that are ready for approval"""

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(liability_waiver_accepted_at__isnull=False)
        qs = qs.filter(membership_activation_completed_at__isnull=True)
        return qs
