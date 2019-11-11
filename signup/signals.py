from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now as tz_now
from .models import Invitation

import datetime

@receiver(pre_save, sender=Invitation)
def add_invitation_timestamps(sender, instance, *args, **kwargs):
    instance.created_at = tz_now()
    instance.expires_at tz_now() + datetime.timedelta(days=14)
