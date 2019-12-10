from django.db import models
from dashboard.models import User

class Capability(models.Model):
    name = models.CharField(max_length=50)
    short_description = models.CharField(max_length=255)
    long_description = models.TextField()

    recipients = models.ManyToManyField(
        User,
        through='Endorsement',
        through_fields=('capability', 'recipient'),
    )

class Endorsement(models.Model):
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipient_set'
    )
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trainer_set'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField('Notes', null=True, blank=True, help_text='Only staff will be able to view these notes')
