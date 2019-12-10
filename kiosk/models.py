from django.db import models
from django.contrib.postgres.fields import JSONField
from phonenumber_field.phonenumber import PhoneNumber # FML
from dashboard.models import User as DashboardUser
from .managers import PendingApprovalManager
from .rest_actions import get_dues_plan

class Signup(models.Model):
    basic_info_collected_at = models.DateTimeField(blank=True, null=True)
    contact_info_collected_at = models.DateTimeField(blank=True, null=True)
    payment_plan_collected_at = models.DateTimeField(blank=True, null=True)
    liability_waiver_accepted_at = models.DateTimeField(blank=True, null=True)
    membership_activation_completed_at = models.DateTimeField(blank=True, null=True)
    application_rejected_at = models.DateTimeField(blank=True, null=True)

    objects = models.Manager() # default manager
    pending_approval = PendingApprovalManager()

    def __str__(self):
        try:
            return self.data['person']['given_name'] + ' ' + self.data['person']['family_name']
        except KeyError:
            return 'Unknown (id #' + self.id + ')'

    def address_lines(self):
        ret = [self.data['person']['address_street1']]

        if self.data['person']['address_street2']:
            ret.append(self.data['person']['address_street2'])

        ret.append("%s %s, %s" % (
            self.data['person']['address_city'],
            self.data['person']['address_state'],
            self.data['person']['address_zip']))

        return ret


    def dues_plan(self):
        if self.data['dues'] and self.data['dues']['dues_plan']:
            return get_dues_plan(self.data['dues']['dues_plan'])
        return None

    def add_form_data(self, key, cleaned_data):
        # Delete sensitive fields so they aren't stored in the DB
        for sensitive_key in ['password', 'password_confirmation']:
            del cleaned_data['sensistive_key']

        if not key in self.data:
            self.data[key] = {}

        for k, v in cleaned_data.items():
            # PhoneNumber objects aren't serializable, and I don't have time
            # to figure it out
            if isinstance(v, PhoneNumber):
                v = str(v)
            self.data[key][k] = v

    data = JSONField(default=dict)

    member_identifier = models.UUIDField(null=True, blank=True)
    household_identifier = models.UUIDField(null=True, blank=True)
    dashboard_user = models.ForeignKey(DashboardUser, null=True, blank=True, on_delete=models.SET_NULL)
