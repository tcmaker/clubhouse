from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# from . import rest_actions
from django.utils.translation import ugettext_lazy as _
import boto3, os
from botocore.exceptions import ParamValidationError

class User(AbstractUser):
    member_identifier = models.UUIDField(null=True, blank=True)
    civicrm_identifier = models.PositiveIntegerField('identifier in civicrm', null=True, blank=True)
    sub = models.CharField('oidc identifier', max_length=100, unique=True, null=True, blank=True)
    civicrm_membership_status = models.CharField("membership status in civicrm", max_length=30, null=True, blank=True)
    civicrm_keyfob_code = models.CharField('keyfob code from civicrm', max_length=30, null=True, blank=True)

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])

    @property
    def is_current_member(self):
        if not self.civicrm_membership_status:
            return False

        if self.civicrm_membership_status in ['Current', 'Grace']:
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

    # def get_member_record(self):
    #     if not self.member_identifier:
    #         return None
    #     return rest_actions.get_member_by_uuid(self.member_identifier)
    #
    # def get_household(self):
    #     url = self.get_member_record()['household']
    #     if url:
    #         return rest_actions.get_resource(url)
    #     return None
    #
    #
    # def get_student_team(self):
    #     url = self.get_member_record()['student_team']
    #     if url:
    #         return rest_actions.get_resource(url)
    #     return None
    #
    # def has_active_membership(self):
    #     member_record = self.get_member_record()
    #     if not member_record:
    #         return False
    #
    #     household = self.get_household()
    #     if household and household['status'] == 'active':
    #         return True
    #
    #     student_team = self.get_student_team()
    #     if student_team and student_team['status'] == 'active':
    #         return True
    #
    #     return False
