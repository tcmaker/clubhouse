import factory
import factory.django
import timeslots.models
import workshop.factories
import accounts.factories
from datetime import datetime

class TimeslotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = timeslots.models.Timeslot
        strategy = 'create'

    start_time = datetime(2030, 12, 31, 12, 0, 0, 0)
    end_time = datetime(2030, 12, 31, 15, 0, 0, 0)
    area = factory.SubFactory(workshop.factories.AreaFactory)

class ExemptTimeslotFactory(TimeslotFactory):
    area = factory.SubFactory(workshop.factories.ExemptAreaFactory)

class ReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = timeslots.models.Reservation
        strategy = 'create'

    member = factory.SubFactory(accounts.factories.CurrentMemberFactory)
    timeslot = factory.SubFactory(TimeslotFactory)

class ExemptReservationFactory(ReservationFactory):
    timeslot = factory.SubFactory(ExemptTimeslotFactory)
