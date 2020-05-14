from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.shortcuts import render, redirect
from workshop.models import Area
from django.utils.dateparse import parse_datetime
from datetime import date, datetime
from .utils import get_timeslots_for_range, get_or_create_timeslot
from .forms import ReservationForm, CancelReservationForm
from .models import Reservation
from django.contrib import messages
from django.core.exceptions import ValidationError

from django.utils.timezone import now as tz_now

import json

def area_list(request):
    context = {
        'areas': Area.objects.all()
    }
    return render(request, 'timeslots/index.html', context)

def area_detail(request, area_id):
    today = date.today()
    months = ["2020-%02d" % m for m in range(today.month, 13)]

    return render(request, 'timeslots/area_detail.html', {
        'area': Area.objects.get(pk=area_id),
        'months': months
    })

def area_calendar(request, area_id):
    return render(request, 'timeslots/area_calendar.html', {
        'area': Area.objects.get(pk=area_id),
    })

def area_calendar_date(request, area_id, date_string):
    return render(request, 'timeslots/area_calendar_date.html', {
        'area': Area.objects.get(pk=area_id),
    })

def events_as_json(request, area_id):
    start = parse_datetime(request.GET['start'])
    end = parse_datetime(request.GET['end'])
    area = Area.objects.get(pk=area_id)
    return HttpResponse(json.dumps(get_timeslots_for_range(area, start, end)), content_type = 'application/json')

def timeslot_detail(request, area_id, slug):
    area = Area.objects.get(pk=area_id)

    return render(request, 'timeslots/timeslot_detail.html', {
        'area': area,
        'timeslot': get_or_create_timeslot(slug),
    })

def reservation_form(request, area_id, slug):

    area = Area.objects.get(pk=area_id)
    timeslot = get_or_create_timeslot(slug)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = Reservation()
            reservation.timeslot = timeslot
            reservation.member = request.user
            try:
                reservation.full_clean()
            except ValidationError as e:
                for msg in e.messages:
                    messages.error(request, msg)
                return HttpResponseRedirect("/timeslots/%d/%s/" % (area.id, timeslot.slug))

            reservation.save()
            messages.success(request, 'Your reservation is good to go')
            return HttpResponseRedirect("/timeslots/")

    else:
        form = ReservationForm()

    return render(request, 'timeslots/reservation.html', {
        'area': area,
        'timeslot': timeslot,
        'form': form,
    })

def reservation_list(request):
    return render(request, 'timeslots/reservation_list.html', {
        'reservations': request.user.reservation_set.order_by('timeslot__start_time')
    })

def reservation_detail(request, reservation_id):
    reservation = request.user.reservation_set.get(pk=reservation_id)

    return render(request, 'timeslots/reservation_detail.html', {
        'reservation': reservation
    })

def reservation_cancel(request, reservation_id):
    reservation = request.user.reservation_set.get(pk=reservation_id)

    if request.method == 'POST':
        form = CancelReservationForm(request.POST)

        if tz_now() >= reservation.timeslot.start_time:
            messages.error(request, "You cannot cancel a reservation once it has started.")
            return HttpResponseRedirect("/timeslots/reservations/" + str(reservation.id) + "/")

        reservation.delete()
        return HttpResponseRedirect("/timeslots/")
    else:
        form = CancelReservationForm(initial={'confirmed': 'true'})

    return render(request, 'timeslots/reservation_cancel.html', {
        'form': form,
        'reservation': reservation
    })
