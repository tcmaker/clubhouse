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

from .civicrm import get_member_info, get_membership_status

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

class User(AbstractUser):
    member_identifier = models.UUIDField(null=True, blank=True)
    civicrm_identifier = models.PositiveIntegerField('identifier in civicrm', null=True, blank=True)
    sub = models.CharField('oidc identifier', max_length=100, unique=True, null=True, blank=True)
    civicrm_membership_status = models.CharField("membership status in civicrm", max_length=30, null=True, blank=True)
    civicrm_keyfob_code = models.CharField('keyfob code from civicrm', max_length=30, null=True, blank=True)

    objects = ClubhouseUserManager()

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])

    @property
    def is_current_member(self):
        if not self.civicrm_membership_status:
            return False

        if self.civicrm_membership_status in ['Current', 'Grace', 'New']:
            return True

        return False

    #### Cognito ####

    @property
    def __cognito_client(self):
        return boto3.client('cognito-idp', region_name=os.environ.get('AWS_DEFAULT_REGION'))

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

    def sync_membership_status(self):
        if not self.civicrm_identifier: return
        self.civicrm_membership_status = get_membership_status(self.civicrm_identifier)
        self.save()

    def sync_membership_info(self):
        if not self.civicrm_identifier:
            return

        info = get_member_info(self.civicrm_identifier)
        self.first_name=info['first_name']
        self.last_name=info['last_name']
        self.email=info['email']
        if 'keyfob' in info:
            self.civicrm_keyfob_code = info['keyfob']
        self.civicrm_membership_status = get_membership_status(self.civicrm_identifier)
        self.save()

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
