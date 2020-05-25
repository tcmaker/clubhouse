from django.test import TestCase
from . import factories
from timeslots.models import User

def UserTestCase(TestCase):
    def test_active_membership_statuses(self):
        user = factories.UserFactory.create()

        for active_status in ['Current', 'Grace', 'New']:
            user.civicrm_membership_status = active_status
            self.assertTrue(user.is_current_member)
