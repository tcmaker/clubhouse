from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
# from . import rest_actions
from django.utils.translation import ugettext_lazy as _
import boto3, os, re, uuid
from botocore.exceptions import ParamValidationError
from django.utils.timezone import now as tz_now
from datetime import timedelta, datetime
from uuid import uuid4

from .civicrm import get_member_info, get_membership_status
from dashboard.civicrm import profile_update_email

from billing.util import api_get, api_patch

import requests

class ClubhouseUserManager(UserManager):
    def _sterilize_for_username(self, s):
        return re.sub(r'[^A-Za-z]', '', s).lower()

    def _make_username(self, first_name, last_name):
        dedup = 2
        base = '.'.join([
            self._sterilize_for_username(first_name),
            self._sterilize_for_username(last_name)
        ])
        candidate = base
        while User.objects.filter(username=candidate).exists():
            candidate = candidate + str(dedup)
            dedup += 1
        return candidate


    def import_member_by_contact_id(self, contact_id):
        if self.filter(civicrm_identifier=int(contact_id)).exists():
            raise ValueError('Member already exists in our database')

        info = get_member_info(contact_id)

        u = User(
            first_name=info['first_name'],
            last_name=info['last_name'],
            email=info['email'],
            username=self._make_username(info['first_name'], info['last_name']),
            civicrm_identifier=str(contact_id),
            # civicrm_membership_status = 'Current',
        )
        if info['keyfob']:
            u.civicrm_keyfob_code = info['keyfob']
        u.save()
        return u

    def import_member_from_billing_system(self, url):
        # TODO: Once migration is complete, check if account already exists

        person = api_get(url)

        if person['household'] is not None:
            household = api_get(person['household'])

        if person['household'] is None:
            household = api_get(person['student_team'])
            household['external_customer_identifier'] = None

        print(person)

        u = User(
            first_name=person['given_name'],
            last_name=person['family_name'],
            email=person['email'],
            username=self._make_username(person['given_name'], person['family_name']),
            membership_person_record = url,
            stripe_customer_identifier = household['external_customer_identifier']
        )
        u.save()
        return u

class User(AbstractUser):
    membership_person_record = models.URLField(null=True, blank=True)
    civicrm_identifier = models.PositiveIntegerField('identifier in civicrm', null=True, blank=True)
    sub = models.CharField('oidc identifier', max_length=100, unique=True, null=True, blank=True)
    civicrm_membership_status = models.CharField("membership status in civicrm", max_length=30, null=True, blank=True)
    civicrm_keyfob_code = models.CharField('keyfob code from civicrm', max_length=30, null=True, blank=True)
    pending_email = models.EmailField('unverified email address', null=True, blank=True)
    pending_email_verification_code = models.UUIDField(null=True, blank=True)
    stripe_customer_identifier = models.CharField('Stripe customer identifier', max_length=100, null=True, blank=True)

    objects = ClubhouseUserManager()

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])

    @property
    def is_enrolled(self):
        person = api_get(self.membership_person_record)

        # student teams don't go through the standard checks
        if person['student_team'] is not None:
            team = api_get(person['student_team'])
            if team['status'] in ['expired', 'canceled']:
                return False
            return True

        household = api_get(person['household'])

        if not household['external_subscription_identifier']:
            print('NO SUBSCRIPTION')
            return False

        if household['status'] in ['expired', 'canceled']:
            return False

        print('USER IS ENROLLED')
        return True

    @property
    def is_current_member(self):
        if not self.membership_person_record:
            return False

        if self.civicrm_membership_status in ['active']:
            return True

        return False

    @property
    def is_inactive_member(self):
        if not self.membership_person_record:
            return False

        if self.civicrm_membership_status in ['Expired', 'canceled', 'past_due', 'unpaid', 'incomplete_expired', 'incomplete', 'Grace']:
            return True

        return False

    def set_pending_email_and_verify(self, email_address):
        self.pending_email = email_address
        self.pending_email_verification_code = uuid4()
        self.save()

        context = {
            'member': self,
            'hostname': settings.WEBAPP_URL_BASE
        }
        msg_html = render_to_string('email/verify_pending_email.html', context)
        msg = EmailMessage(subject='Twin Cities Maker: Verify Your Email', body=msg_html, to=[self.pending_email])
        msg.content_subtype = "html"  # Main content is now text/html
        print("about to send message")
        print(msg.send())
        print("just sent message")

    def verify_pending_email_address(self):
        """It's on you to actually make sure this checks out."""
        self.email = self.pending_email
        self.pending_email = None
        self.pending_email_verification_code = None
        self.save()
        self.update_civicrm_with_email()
        self.sync_cognito_user_attributes()

    #### Cognito ####
    @property
    def __cognito_client(self):
        return boto3.client('cognito-idp', region_name=os.environ.get('AWS_DEFAULT_REGION'))

    def sync_cognito_user_attributes(self):
        user_attributes =[
            {'Name': 'email', 'Value': self.email},
            {'Name': 'family_name', 'Value': self.last_name},
            {'Name': 'given_name', 'Value': self.first_name},
            {'Name': 'email_verified', 'Value': 'True'},
        ]

        response = self.__cognito_client.admin_update_user_attributes(
            UserPoolId = settings.COGNITO_USER_POOL_ID,
            Username=self.username,
            UserAttributes = user_attributes
        )
        return response

    def change_cognito_password(self, new_password, is_temporary=False):
        try:
            response = self.__cognito_client.admin_set_user_password(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=self.username,
                Password=new_password,
                Permanent= not is_temporary
            )
            return response
        except ParamValidationError as e:
            raise ArgumentError('Password requirements not met')

    def get_cognito_record(self):
        response = self.__cognito_client.admin_get_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=self.username
        )
        if self.sub is None:
            for attribute in response['UserAttributes']:
                if attribute['Name'] == 'sub':
                    self.sub = attribute['Value']
                    self.save()
                    break
        return response

    def cognito_reset_temporary_password(self):

        # Does the user have a temporary password?
        if not self.get_cognito_record()['UserStatus'] == 'FORCE_CHANGE_PASSWORD':
            raise ValueError('User does not have a temporary password')

        return self.__cognito_client.admin_create_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=self.username,
            MessageAction='RESEND'
        )

    def create_cognito_record(self, email_verified=False):
        user_attributes =[
            {'Name': 'email', 'Value': self.email},
            {'Name': 'family_name', 'Value': self.last_name},
            {'Name': 'given_name', 'Value': self.first_name},
            {'Name': 'preferred_username', 'Value': self.username},
        ]

        if (email_verified):
            user_attributes.append({'Name': 'email_verified', 'Value': 'True'})

        response = self.__cognito_client.admin_create_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=self.username,
            UserAttributes=user_attributes,
            DesiredDeliveryMediums=['EMAIL']
        )
        for attribute in response['User']['Attributes']:
            if attribute['Name'] == 'sub':
                self.sub = attribute['Value']
                self.save()

        return response

    def create_cognito_record_with_password(self, password):
        user_attributes = [
            {'Name': 'email', 'Value': self.email},
            {'Name': 'family_name', 'Value': self.last_name},
            {'Name': 'given_name', 'Value': self.first_name},
            {'Name': 'preferred_username', 'Value': self.username},
            {'Name': 'email_verified', 'Value': 'True'},
        ]

        response = self.__cognito_client.admin_create_user(
            UserPoolId=os.environ['COGNITO_USER_POOL_ID'],
            Username=self.username,
            UserAttributes=user_attributes,
            MessageAction='SUPPRESS' # Don't send a welcome message.
        )

        for attribute in response['User']['Attributes']:
            if attribute['Name'] == 'sub':
                self.sub = attribute['Value']
                self.save()
                break

        return (response, self.change_cognito_password(password))

    ### CiviCRM ###
    def sync_membership_status(self):
        person = api_get(self.membership_person_record)
        if person['household'] is not None:
            household = api_get(person['household'])
        else:
            household = api_get(person['student_team'])

        self.civicrm_membership_status = household['status']

        print(self.civicrm_membership_status)

        self.save()

    def sync_membership_info(self):
        if not self.membership_person_record:
            return

        person = api_get(self.membership_person_record)
        household = api_get(person['household'])

        self.first_name = person['given_name']
        self.last_name = person['family_name']
        self.civicrm_membership_status = household['status']
        self.save()

    def update_civicrm_with_email(self):
        api_patch(self.membership_person_record, json={
            'email': self.email
        })

def two_weeks_from_now():
    return tz_now() + timedelta(days=14)

class Invitation(models.Model):
    uuid = models.UUIDField('Invite Code', default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    expires_at = models.DateTimeField('Expires At', default=two_weeks_from_now)
    accepted_at = models.DateTimeField('Accepted At', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

@receiver(post_save, sender=Invitation)
def send_invite_email(sender, instance, *args, **kwargs):
    # Delete old invites
    for invite in Invitation.objects.filter(user_id=instance.user_id).exclude(pk=instance.id).all():
        invite.delete()

    # Send invite email
    if kwargs['created'] == True:
        context = {
            'invitation': instance,
            'hostname': settings.WEBAPP_URL_BASE
        }
        msg_html = render_to_string('email/invite_member_to_clubhouse.html', context)
        msg = EmailMessage(subject='Register for Twin Cities Maker', body=msg_html, to=[instance.user.email])
        msg.content_subtype = "html"  # Main content is now text/html
        print("about to send message")
        print(msg.send())
        print("just sent message")
