from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
# from . import rest_actions
from django.utils.translation import ugettext_lazy as _
import boto3, os, re
from botocore.exceptions import ParamValidationError

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
    def change_cognito_password(self, new_password, is_temporary=False):
        client = boto3.client('cognito-idp', region_name=os.environ['AWS_DEFAULT_REGION'])
        try:
            response = client.admin_set_user_password(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=self.username,
                Password=new_password,
                Permanent= not is_temporary
            )
            return response
        except ParamValidationError as e:
            raise ArgumentError('Password requirements not met')


    def create_cognito_record(self, email_verified=False):
        user_attributes =[
            {'Name': 'email', 'Value': self.email},
            {'Name': 'family_name', 'Value': self.last_name},
            {'Name': 'given_name', 'Value': self.first_name},
            {'Name': 'preferred_username', 'Value': self.username},
        ]

        if (email_verified):
            user_attributes.append({'Name': 'email_verified', 'Value': 'True'})

        client = boto3.client('cognito-idp', region_name=os.environ['AWS_DEFAULT_REGION'])
        response = client.admin_create_user(
            UserPoolId=os.environ['COGNITO_USER_POOL_ID'],
            Username=self.username,
            UserAttributes=user_attributes,
            DesiredDeliveryMediums=['EMAIL']
        )
        for attribute in response['User']['Attributes']:
            if attribute['Name'] == 'sub':
                self.sub = attribute['Value']
                self.save()

        return response

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
