from django.db import models, DataError
from django.core.exceptions import ValidationError
from dashboard.models import User
from workshop.models import Area

from django.utils.timezone import timedelta, localtime

SLUG_STRFTIME_FORMAT = "%Y%m%d%H%M"
HUMANIZED_TIME_FORMAT = "%-I:%M %p"
HUMANIZED_DATE_FORMAT = "%h %d, %Y"

MEMBER_MAX_DAILY_TIMESLOTS = 1

class Timeslot(models.Model):
    start_time = models.DateTimeField('Start Time', blank=False, null=False)
    end_time = models.DateTimeField('End Time', blank=False, null=False)
    slug = models.CharField('Timeslot Text Key', max_length=100, editable=False, null=False, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=False, null=False)

    def has_capacity(self):
        return self.area.covid19_capacity > self.reservation_set.count()

    def __str__(self):
        return self.humanize(include_date=True, include_area=True)

    # set slug on save
    def save(self, *args, **kwargs):
        self.end_time = self.start_time + timedelta(hours=2)

        slug = [
            str(self.area.id),
            self.start_time.strftime(SLUG_STRFTIME_FORMAT),
            self.end_time.strftime(SLUG_STRFTIME_FORMAT),
        ]
        self.slug = "-".join(slug)

        if (self.start_time.hour % 2 != 0):
            raise DataError('Timeslots cannot have odd-numbered hours')

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

class Reservation(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    timeslot = models.ForeignKey('Timeslot', on_delete=models.CASCADE, blank=False, null=False)

    def __timeslot_is_available(self):
        area_max_capacity = self.timeslot.area.covid19_capacity
        reserved_capacity = self.timeslot.reservation_set.count()
        # import code; code.interact(local=dict(globals(), **locals()))
        return area_max_capacity > reserved_capacity

    def __member_has_open_reservations(self):
        # start_of_day = localtime(self.timeslot.start_time).replace(hour=0, minute=0, second=0, microsecond=0)
        # end_of_day = localtime(self.timeslot.end_time).replace(hour=23, minute=59, second=59, microsecond=999)
        total = Reservation.objects
        total = total.filter(timeslot__start_time__date=self.timeslot.start_time.date())
        total = total.filter(member_id=self.member.id).count()


        # import code; code.interact(local=dict(globals(), **locals()))

        return MEMBER_MAX_DAILY_TIMESLOTS > total

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
