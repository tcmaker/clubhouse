from datetime import date, datetime, timedelta
from calendar import HTMLCalendar
from .models import Timeslot, SLUG_STRFTIME_FORMAT, LENGTH_OF_TIMESLOT
from workshop.models import Area
from collections import deque
from django.utils.timezone import now as tz_now

import pytz

def parse_date_string(date_string):
    return datetime.strptime('%Y-%m-%d', date_string).date()

# HACK: Do this correctly when stuff settles down
def datetimes_are_equal(left, right):
    if left.year == right.year and left.month == right.month and left.day == right.day and left.hour == right.hour:
        return True
    return False

def close_area_by_date_range(area, start_time, end_time):
        json = get_timeslots_for_range(area, start_time, end_time)
        timeslots = []
        for json_object in json:
            timeslot = get_or_create_timeslot(json_object['id'])
            timeslot.is_closed_by_staff = True
            timeslot.save()
            timeslot.cancel_reservations(True)
            timeslots.append(timeslot)
        return timeslots

def open_area_by_date_range(area, start_time, end_time):
    json = get_timeslots_for_range(area, start_time, end_time)
    timeslots = []
    for json_object in json:
        timeslot = get_or_create_timeslot(json_object['id'])
        timeslot.is_closed_by_staff = False
        timeslot.save()
        timeslots.append(timeslots)
    return timeslots

def activate_riot_mode(start_time, end_time):
    for area in Area.objects.all():
        timeslots = close_area_by_date_range(area, start_time, end_time)
        for timeslot in timeslots:
            print(timeslot.humanize(include_date=True, include_area=True))


def get_timeslots_for_range(area, start_time, end_time):
    models = deque(area.timeslot_set.filter(start_time__gte=start_time, end_time__lte=end_time).order_by('start_time').all())

    # Make dummy records for empty timeslots
    start_hour = start_time.hour
    start_hour -= start_hour % LENGTH_OF_TIMESLOT

    time_counter = start_time.replace(second=0, microsecond=0, minute=0, hour=start_hour)

    timeslots = []

    tz = pytz.timezone('America/Chicago')
    now = tz_now().replace(tzinfo=tz)

    while time_counter < end_time:
        # if time_counter.day == 11 and time_counter.hour == 4:
        #     import code; code.interact(local=dict(globals(), **locals()))

        timeslot_end_time = time_counter + timedelta(hours=LENGTH_OF_TIMESLOT)

        # Does the timeslot already exist?
        # if len(models) > 0 and models[0].start_time == time_counter:
        if len(models) > 0 and datetimes_are_equal(models[0].start_time, time_counter):
            model = models.popleft()
            timeslot = {
                'id': model.slug,
                'start': model.start_time,
                'end':  model.end_time,
            }
            if model.has_capacity():
                timeslot['title'] = 'Available'
            else:
                timeslot['rendering'] = 'background'
                timeslot['className'] = 'timeslots-timeslot-full'
        else:
            # Make a virtual timeslot
            timeslot = {
                'start': time_counter,
                'end': timeslot_end_time,
                'title': 'Available'
            }
            timeslot['id'] = '-'.join([
                str(area.id),
                timeslot['start'].strftime(SLUG_STRFTIME_FORMAT),
                timeslot['end'].strftime(SLUG_STRFTIME_FORMAT),
            ])

        if timeslot['start'].replace(tzinfo=tz) < now:
            timeslot['rendering'] = 'background'
            timeslot['className'] = 'timeslots-timeslot-past'
            if 'title' in timeslot: del timeslot['title']

        timeslot['start'] = str(timeslot['start'])
        timeslot['end'] = str(timeslot['end'])
        timeslots.append(timeslot)
        time_counter = timeslot_end_time

    return timeslots

# def get_open_timeslots_for_date(area, date):
#
#     max_capacity = area.covid19_capacity
#
#     full_slots = area.timeslot_set.filter(start_time__date=date).all()
#     full_slots = [x.start_time for x in full_slots if not x.has_capacity()]
#
#     time_counter = datetime.combine(date, datetime.min.time())
#     end_of_day = datetime.combine(date, datetime.max.time())
#
#     timeslots = []
#     while time_counter < end_of_day:
#         timeslot = {
#             'start': time_counter,
#             'end': 'Open Timeslot'
#         }
#         if time_counter not in full_slots:
#             timeslots.append(timeslot)
#         time_counter += timedelta(hours = 2)
#         timeslot['end_time'] = time_counter
#
#     return timeslots

def get_or_create_timeslot(slug):
    try:
        return Timeslot.objects.get(slug=slug)
    except Timeslot.DoesNotExist:
        parts = slug.split('-')
        area = Area.objects.get(pk=parts[0])
        start_time = datetime.strptime(parts[1], SLUG_STRFTIME_FORMAT)
        end_time = datetime.strptime(parts[2], SLUG_STRFTIME_FORMAT)
        return area.timeslot_set.create(
            start_time = datetime.strptime(parts[1], SLUG_STRFTIME_FORMAT),
            end_time = datetime.strptime(parts[2], SLUG_STRFTIME_FORMAT)
        )
