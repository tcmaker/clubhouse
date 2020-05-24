from django.db import models

from accounts.models import User

class Area(models.Model):
    name = models.CharField('Area Name', max_length=50, null=False, blank=False)
    covid19_capacity = models.PositiveIntegerField('Maximum Concurrent Users')
    area_manager = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    shop_contact_email = models.EmailField(max_length=50, null=True, blank=True)
    is_exempt_from_member_timeslot_quota = models.BooleanField("Reservations in this area do not count against a member's daily quota.", null=False, default=False)

    def __str__(self):
        return self.name
