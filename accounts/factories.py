import factory
import factory.django
from . import models

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    first_name = 'Testy'
    last_name = 'Testuser'
    email = factory.Sequence(lambda n: 'test%d@example.com' % n)
    username = factory.Sequence(lambda n: 'test%d' % n)

class CurrentMemberFactory(UserFactory):
    civicrm_membership_status = 'Current'
    civicrm_identifier = factory.Sequence(lambda n: 50000 + n)
    civicrm_keyfob_code = factory.Sequence(lambda n: 70000 + n)

class StaffUserFactory(CurrentMemberFactory):
    is_staff = True
