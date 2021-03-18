from django.test import TestCase
from . import factories
from timeslots.models import Reservation, MEMBER_MAX_DAILY_TIMESLOTS

class ReservationTestCase(TestCase):
    # def test_member_cannot_create_four_reservations_in_one_day(self):
    #     for reservation in range(0, MEMBER_MAX_DAILY_TIMESLOTS - 0):
    #         print(reservation)
    #         factories.ReservationFactory.create()
    #
    #     standard_reservation = factories.ReservationFactory.create()
    #     user = standard_reservation.member
    #     timeslot = standard_reservation.timeslot
    #
    #     with self.assertRaises(Exception):
    #         illegal_reservation = Reservation.objects.create(
    #             timeslot=timeslot,
    #             member=user
    #         )

    def test_member_can_create_reservation_in_exempt_area(self):
        standard_reservation = factories.ReservationFactory.create()
        user = standard_reservation.member
        timeslot = standard_reservation.timeslot

        r = Reservation.objects.create(
            timeslot = factories.ExemptTimeslotFactory.create(),
            member = user
        )

        self.assertIsInstance(r, Reservation)

    def test_exempt_reservation_does_not_block_reservation(self):
        exempt_reservation = factories.ExemptReservationFactory.create()
        user = exempt_reservation.member
        timeslot = exempt_reservation.timeslot

        r = Reservation.objects.create(
            member = user,
            timeslot = factories.TimeslotFactory.create()
        )

        self.assertIsInstance(r, Reservation)
