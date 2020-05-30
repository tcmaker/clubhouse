from django.db import models
from accounts.models import User
from django.utils.timezone import now as tz_now

# class CubbyRequest(models.Model):
#     member = models.ForeignKey(User, on_delete=models.CASCADE)
#     requested_at = models.DateTimeField(default=tz_now)
#
#     def __str__(self):
#         return "%s %s" % (member.first_name, member.last_name)

class Cubby(models.Model):
    aisle = models.CharField(max_length=5)
    identifier = models.CharField(max_length=5)
    assignee = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "cubbies"

    def __str__(self):
        return 'Aisle %s, Cubby %s' % (self.aisle, self.identifier)

# GREEN_TAG_STATUSES = [
#     ('active', 'Active'),
#     ('expired', 'Expired'),
#     ('noncompliant', 'Non-Compliant'),
#     ('closed', 'Closed'),
# ]
#
# RED_TAG_STATUSES = [
#     ('reported', 'Reported'),
#     ('verified', 'Verified'),
#     ('invalid', 'Invalid'),
#     ('resolved', 'Resolved'),
# ]

# class GreenTag(models.Model):
#     title = models.CharField(max_length=100)
#     assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='green_tags_issued')
#     location = models.CharField(max_length=200)
#     issued_at = models.DateTimeField(default=tz_now)
#     description = models.TextField()
#     status = models.CharField(max_length=40, choices=GREEN_TAG_STATUSES)
#
#     def __str__(self):
#         return self.title

# class RedTag(models.Model):
#     title = models.CharField(max_length=100)
#     reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='red_tags_created')
#     violator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='red_tag_violations')
#     location = models.CharField(max_length=200)
#     description = models.TextField()
#     issued_at = models.DateTimeField(default=tz_now)
#     violator_notified_at = models.DateTimeField(null=True, blank=True)
#     green_tag = models.ForeignKey(GreenTag, null=True, blank=True, on_delete=models.SET_NULL)
#     cubby = models.ForeignKey(Cubby, null=True, blank=True, on_delete=models.SET_NULL)
#     status = models.CharField(max_length=40, choices=RED_TAG_STATUSES)
#
#     def __str__(self):
#         return self.title
