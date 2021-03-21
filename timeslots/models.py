from django.db import models, DataError
from django.core.exceptions import ValidationError
from accounts.models import User
from workshop.models import Area
from django.utils.timezone import now as tz_now

from django.core.mail import send_mail

from django.utils.timezone import timedelta, localtime

SLUG_STRFTIME_FORMAT = "%Y%m%d%H%M"
HUMANIZED_TIME_FORMAT = "%-I:%M %p"
HUMANIZED_DATE_FORMAT = "%h %d, %Y"

ENFORCE_MAX_CAPACITY=True

LENGTH_OF_TIMESLOT = 1

MEMBER_MAX_DAILY_TIMESLOTS = 3

CANCEL_RESERVATION_TEXT = '''%s,

Our records show that you have reserved the following time in the %s:

* %s

Unfortunately, the %s area manager has closed the shop during this time,
either for maintenance or to schedule a class, and your reservation has been
canceled. Unless notified otherwise, none of your other reservations have been
affected, and you are welcome to show up during those timeslots as you normally
would.

We're sorry for the inconvenience this causes and promise to keep these
cancelations to an absolute minimum.

Thanks for your patience!

Twin Cities Maker
'''

class Timeslot(models.Model):
    start_time = models.DateTimeField('Start Time', blank=False, null=False)
    end_time = models.DateTimeField('End Time', blank=False, null=False)
    slug = models.CharField('Timeslot Text Key', max_length=100, editable=False, null=False, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=False, null=False)
    is_closed_by_staff = models.BooleanField('Area is closed for class or maintenance', null=False, default=False)

    def cancel_reservations(self, notify_members=True):
        for reservation in self.reservation_set.all():
            if notify_members == True:
                send_mail(
                    'Twin Cities Maker: %s Reservation' % self.area.name,
                    CANCEL_RESERVATION_TEXT % (
                        reservation.member.first_name,
                        self.area.name,
                        self.humanize(include_date=True),
                        self.area.name),
                    'membership@tcmaker.org',
                    [reservation.member.email],
                )
            reservation.delete()

    def reservation_count(self):
        return self.reservation_set.count()

    def has_capacity(self):
        if self.is_closed_by_staff: return False
        return self.area.covid19_capacity > self.reservation_set.count()

    def __str__(self):
        return self.humanize(include_date=True, include_area=True)

    # set slug on save
    def save(self, *args, **kwargs):
        self.end_time = self.start_time + timedelta(hours=LENGTH_OF_TIMESLOT)

        slug = [
            str(self.area.id),
            self.start_time.strftime(SLUG_STRFTIME_FORMAT),
            self.end_time.strftime(SLUG_STRFTIME_FORMAT),
        ]
        self.slug = "-".join(slug)

        if (self.start_time.hour % LENGTH_OF_TIMESLOT != 0):
            raise DataError('Timeslots must be divisible by LENGTH_OF_TIMESLOT')

        if (self.start_time.minute != 0 or self.start_time.second != 0):
            raise DataError('Timeslots must start at the beginning of the hour')


        return super().save(*args, **kwargs)

    # convenience helper to display time in a friendly way
    def humanize(self, include_date=False, include_area=False):
        ret = "%s - %s" % (
            self.start_time.strftime(HUMANIZED_TIME_FORMAT),
            self.end_time.strftime(HUMANIZED_TIME_FORMAT)
        )

        if include_date:
            ret = self.start_time.strftime(HUMANIZED_DATE_FORMAT) + ": " + ret

        if include_area:
            ret += " (%s)" % self.area.name

        return ret

class ReservationManager(models.Manager):
    def upcoming(self):
        return self.get_queryset().order_by('timeslot__start_time').filter(timeslot__end_time__gte=tz_now())

class Reservation(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    timeslot = models.ForeignKey('Timeslot', on_delete=models.CASCADE, blank=False, null=False)

    objects = ReservationManager()

    def as_text_with_date(self):
        return self.timeslot.humanize(include_date=True)

    def as_text_with_date_and_area(self):
        return self.timeslot.humanize(include_date=True, include_area=False)

    def __timeslot_is_available(self):
        if not ENFORCE_MAX_CAPACITY:
            return True
        area_max_capacity = self.timeslot.area.covid19_capacity
        reserved_capacity = self.timeslot.reservation_set.count()
        # import code; code.interact(local=dict(globals(), **locals()))
        return area_max_capacity > reserved_capacity

    def __member_has_open_reservations(self):
        if self.timeslot.area.is_exempt_from_member_timeslot_quota:
            return True

        total = Reservation.objects
        total = total.filter(
            timeslot__start_time__date=self.timeslot.start_time.date(),
            timeslot__area__is_exempt_from_member_timeslot_quota=False
        )
        total = total.filter(member_id=self.member.id).count()
        return total < MEMBER_MAX_DAILY_TIMESLOTS

        return MEMBER_MAX_DAILY_TIMESLOTS > total

    def __member_is_attempting_to_double_book(self):
        pass

    def clean(self):
        if not self.__member_has_open_reservations():
            raise ValidationError({
                'timeslot': 'Member has already booked a timeslot for this day.',
            })

        if not self.__timeslot_is_available():
            raise ValidationError({
                'timeslot': 'The timeslot is already full',
            })

        return super().clean()

    def save(self, *args, **kwargs):
        if not self.__member_has_open_reservations():
            raise DataError('Member has already booked a timeslot for this day.')

        if not self.__timeslot_is_available():
            raise DataError('The timeslot is already full')

        return super().save(*args, **kwargs)
