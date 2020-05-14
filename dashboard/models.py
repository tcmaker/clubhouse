from django.db import models
from django.contrib.auth.models import AbstractUser
from . import rest_actions

class User(AbstractUser):
    member_identifier = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])

    def get_member_record(self):
        if not self.member_identifier:
            return None
        return rest_actions.get_member_by_uuid(self.member_identifier)

    def get_household(self):
        url = self.get_member_record()['household']
        if url:
            return rest_actions.get_resource(url)
        return None


    def get_student_team(self):
        url = self.get_member_record()['student_team']
        if url:
            return rest_actions.get_resource(url)
        return None

    def has_active_membership(self):
        member_record = self.get_member_record()
        if not member_record:
            return False

        household = self.get_household()
        if household and household['status'] == 'active':
            return True

        student_team = self.get_student_team()
        if student_team and student_team['status'] == 'active':
            return True

        return False
