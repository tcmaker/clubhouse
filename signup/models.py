
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils.timezone import now as tz_now
from django.dispatch import receiver
#from membership.models import Member, Membership
from billing.util import api_patch, api_post
from signup.managers import ActiveInviteManager, PendingApprovalManager
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
import uuid, datetime
from django.conf import settings
from accounts.models import User
from phonenumber_field.modelfields import PhoneNumberField
from localflavor.us.models import USStateField, USZipCodeField

import requests

class Applicant(models.Model):
    # Basic Information
    given_name = models.CharField('First Name', max_length=40, blank=False)
    family_name = models.CharField('Last Name', max_length=40, blank=False)
    email = models.EmailField('Email Address', blank=False)

    # Address
    address_street1 = models.CharField('Street Address', max_length=100, blank=True, null=True)
    address_street2 = models.CharField('Street Address 2', max_length=100, blank=True, null=True)
    address_city = models.CharField('City', max_length=100, blank=True, null=True)
    address_state = USStateField('State', blank=True, null=True)
    address_zip = USZipCodeField('Zip Code', blank=True, null=True)

    # Phone Number
    phone_number = PhoneNumberField(blank=True, null=True)
    phone_can_receive_sms = models.BooleanField(null=False, default=False)

    # Emergency Contact Info
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = PhoneNumberField(blank=True, null=True)

    # Just in case
    keyfob_code = models.CharField(max_length=50, blank=True, null=True)

    # Links to related records
    civicrm_identifier = models.CharField('CiviCRM Contact ID', max_length=6, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Holds invite code
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=False)

    # Applicant performs these steps
    basic_info_collected_at = models.DateTimeField(blank=True, null=True)
    contact_info_collected_at = models.DateTimeField(blank=True, null=True)
    liability_waiver_accepted_at = models.DateTimeField(blank=True, null=True)
    application_completed_at = models.DateTimeField(blank=True, null=True)

    # TCMaker Staff performs these steps
    keyfob_issued_at = models.DateTimeField(blank=True, null=True)
    account_invitation_created_at = models.DateTimeField(blank=True, null=True)

    # After orientation, applicant completes these steps
    account_invitation_accepted_at = models.DateTimeField(blank=True, null=True)
    account_created_at = models.DateTimeField(blank=True, null=True)
    membership_completed_at = models.DateTimeField(blank=True, null=True)

    # Managers
    objects = models.Manager() # default manager
    pending = PendingApprovalManager()

    class Meta:
        abstract = True

    def send_invitation_email(self):
        context = {
            'registration': self,
            'hostname': settings.WEBAPP_URL_BASE
        }
        msg_html = render_to_string('signup/email/invitation.html', context)
        msg = EmailMessage(subject='Twin Cities Maker: Complete Your Registration', body=msg_html, to=[self.email])
        msg.content_subtype = "html"  # Main content is now text/html
        print("about to send message")
        print(msg.send())
        print("just sent message")

class Registration(Applicant):
    payment_plan_collected_at = models.DateTimeField(blank=True, null=True)
    payment_info_collected_at = models.DateTimeField(blank=True, null=True)
    paid_setup_fee_at = models.DateTimeField(blank=True, null=True)
    invitation_screen_passed_at = models.DateTimeField(blank=True, null=True)
    membership_person_record = models.URLField(blank=True, null=True)
    membership_household_record = models.URLField(blank=True, null=True)
    stripe_identifier = models.CharField('Stripe Customer ID', max_length=30, blank=True, null=True, unique=True)

    def address_lines(self):
        ret = [self.address_street1]

        if self.address_street2:
            ret.append(self.address_street2)

        ret.append("%s %s, %s" % (
            self.address_city,
            self.address_state,
            self.address_zip))

        return ret

    def __str__(self):
        return ' '.join([
            self.given_name,
            self.family_name,
        ])

    def upload_to_billing_system(self):
        # Create Person from applicant
        person = api_post(settings.BILLING_SYSTEM_API_URL + 'persons/', json={
            'family_name': self.family_name,
            'given_name': self.given_name,
            'email': self.email,
            'address_street1': self.address_street1,
            'address_city': self.address_city,
            'address_state': self.address_state,
            'address_zip': self.address_zip,
            'phone_number': str(self.phone_number),
            # 'phone_can_receive_sms': self.phone_can_receive_sms,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': str(self.emergency_contact_phone),
        })
        print(person)

        # Create Household from applicant
        household = api_post(settings.BILLING_SYSTEM_API_URL + 'households/', json={
            'name': "%s %s's Household" % (self.given_name, self.family_name),
            'contact': person['url'],
            'external_customer_identifier': self.stripe_identifier,
        })

        print(household)

        # Add member to household (they are currently just the contact)
        resp = api_patch(person['url'], json={
            'household': household['url'],
        })

        self.membership_person_record = person['url']
        self.membership_household_record = household['url']
        self.save()

    def upload_keyfob_to_billing_system(self):
        keyfob = api_post(settings.BILLING_SYSTEM_API_URL + 'keyfobs/', json={
            'person': self.membership_person_record,
            'code': self.keyfob_code,
            'access_level': 1,
            'is_active': True,
        })
        print(keyfob)

def two_weeks_from_now():
    return tz_now() + datetime.timedelta(days=14)

# class Invitation(Applicant):
#     plus_one_of = models.ForeignKey(Registration, on_delete=models.SET_NULL, blank=True, null=True)
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(default=two_weeks_from_now)
#     accepted_at = models.DateTimeField(blank=True, null=True)
#
#     # Managers
#     active = ActiveInviteManager() # Invites that are waiting to be used
#
# @receiver(post_save, sender=Invitation)
# def send_invite_email(sender, instance, *args, **kwargs):
#     if kwargs['created'] == True:
#         context = {
#             'invitation': instance,
#             'hostname': settings.WEBAPP_URL_BASE
#         }
#         msg_html = render_to_string('signup/email/invitation.html', context)
#         msg = EmailMessage(subject='Register for Twin Cities Maker', body=msg_html, to=[instance.email])
#         msg.content_subtype = "html"  # Main content is now text/html
#         print("about to send message")
#         print(msg.send())
#         print("just sent message")
