from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.db.models.signals import post_save
from django.utils.timezone import now as tz_now
from django.dispatch import receiver
from membership.models import Member, Membership
from signup.managers import ActiveInviteManager, PendingApprovalManager
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
import uuid, datetime
from django.conf import settings

class Applicant(models.Model):
    basic_info_collected_at = models.DateTimeField(blank=True, null=True)
    contact_info_collected_at = models.DateTimeField(blank=True, null=True)
    liability_waiver_accepted_at = models.DateTimeField(blank=True, null=True)
    membership_activation_completed_at = models.DateTimeField(blank=True, null=True)
    application_rejected_at = models.DateTimeField(blank=True, null=True)

    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, blank=True, null=True)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True)

    data = HStoreField(default=dict)

    # Managers
    objects = models.Manager() # default manager
    pending_approval = PendingApprovalManager()

    def add_form_data(self, cleaned_data):
        for k, v in cleaned_data.items():
            self.data[k] = v

    def __str__(self):
        if self.basic_info_collected_at != None:
            return ' '.join([self.data['given_name'], self.data['family_name']])
        else:
            return super().__str__()

    def address_lines(self):
        ret = [self.data['address_street1']]

        if self.data['address_street2']:
            ret.append(self.data['address_street2'])

        ret.append("%s %s, %s" % (
            self.data['address_city'],
            self.data['address_state'],
            self.data['address_zip']))

        return ret

    class Meta:
        abstract = True

class SignupProgress(Applicant):
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, blank=True, null=True)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True)
    payment_plan_collected_at = models.DateTimeField(blank=True, null=True)
    payment_info_collected_at = models.DateTimeField(blank=True, null=True)
    invitation_screen_passed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "signup progress records"

def two_weeks_from_now():
    return tz_now() + datetime.timedelta(days=14)

class Invitation(Applicant):
    given_name = models.CharField('First Name', max_length=40)
    family_name = models.CharField('Last Name', max_length=40)
    email = models.EmailField('Email Address')
    signup_progress = models.ForeignKey(SignupProgress, on_delete=models.SET_NULL, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=two_weeks_from_now)
    accepted_at = models.DateTimeField(blank=True, null=True)

    # Managers
    active = ActiveInviteManager() # Invites that are waiting to be used

@receiver(post_save, sender=Invitation)
def send_invite_email(sender, instance, *args, **kwargs):
    if kwargs['created'] == True:
        context = {
            'invitation': instance,
            'hostname': settings.WEBAPP_URL_BASE
        }
        msg_html = render_to_string('signup/email/invitation.html', context)
        msg = EmailMessage(subject='Register for Twin Cities Maker', body=msg_html, to=[instance.email])
        msg.content_subtype = "html"  # Main content is now text/html
        print("about to send message")
        print(msg.send())
        print("just sent message")
