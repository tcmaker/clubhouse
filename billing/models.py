from django.db import models

from accounts.models import User

class SubscriptionProgress(models.Model):
    initialized_subscription_at = models.DateTimeField()
    chose_collection_method_at = models.DateTimeField()
    entered_payment_method_at = models.DateTimeField()
    completed_subscription_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    prefers_autopay = models.BooleanField()

    def __str__(self):
        return " ".join([user.first_name, user.last_name])
