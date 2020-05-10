from django.db import models

from dashboard.models import User

class Area(models.Model):
    name = models.CharField('Area Name', max_length=50, null=False, blank=False)
    covid19_capacity = models.PositiveIntegerField('Maximum Concurrent Users')
    area_manager = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name
