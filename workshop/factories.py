import factory
import factory.django
from . import models
import accounts.factories

class AreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Area

    name = 'Standard Area'
    covid19_capacity = 3
    area_manager = factory.SubFactory(accounts.factories.StaffUserFactory)
    shop_contact_email = 'area@example.com'
    is_exempt_from_member_timeslot_quota = False

class ExemptAreaFactory(AreaFactory):
    name = 'Exempt Area'
    is_exempt_from_member_timeslot_quota = True
