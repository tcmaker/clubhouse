from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.shortcuts import render, redirect
from workshop.models import Area
from django.utils.dateparse import parse_datetime
from datetime import date, datetime
from .utils import get_timeslots_for_range, get_or_create_timeslot
from .forms import ReservationForm, CancelReservationForm, TimeslotForm
from .models import Reservation
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.timezone import now as tz_now

from django.contrib.auth.decorators import login_required
from accounts.auth.decorators import membership_required

import json

@login_required
@membership_required
def area_list(request):
    context = {
        'areas': Area.objects.order_by('name').all(),
    }
    return render(request, 'timeslots/index.html', context)

@login_required
@membership_required
def area_calendar(request, area_id):
    return render(request, 'timeslots/area_calendar.html', {
        'area': Area.objects.get(pk=area_id),
    })

@login_required
@membership_required
def close_timeslot(request, area_id, slug):
    area = Area.objects.get(pk=area_id)
    timeslot = get_or_create_timeslot(slug)

    # HACK: do it right with roles, etc
    if request.user.id != area.area_manager.id:
        messages.error(request, 'Only the %s manager can do that' % area.name)
        return redirect('/timeslots')

    if request.method == 'POST':
        form = TimeslotForm(request.POST, instance=timeslot)
        try:
            form.save()
            if form.cleaned_data['is_closed_by_staff']:
                # Cancel existing reservations
                timeslot.cancel_reservations(notify_members=True)
            return HttpResponseRedirect("/timeslots/%d/%s/" % (area.id, timeslot.slug))
        except ValueError as e:
            pass
    else:
        form = TimeslotForm(instance=timeslot)

    return render(request, 'timeslots/timeslot_close.html', {
        'area': area,
        'timeslot': timeslot,
        'form': form
    })


@login_required
@membership_required
def events_as_json(request, area_id):
    start = parse_datetime(request.GET['start'])
    end = parse_datetime(request.GET['end'])
    area = Area.objects.get(pk=area_id)
    return HttpResponse(json.dumps(get_timeslots_for_range(area, start, end)), content_type = 'application/json')

@login_required
@membership_required
def timeslot_detail(request, area_id, slug):
    area = Area.objects.get(pk=area_id)
    timeslot = get_or_create_timeslot(slug)

    if (request.user == area.area_manager.id):
        if request.method == POST:
            pass

    return render(request, 'timeslots/timeslot_detail.html', {
        'area': area,
        'timeslot': get_or_create_timeslot(slug),
        'show_manager_options': request.user.id == area.area_manager.id
    })

@login_required
@membership_required
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

@login_required
@membership_required
def reservation_list(request):
    return render(request, 'timeslots/reservation_list.html', {
        'reservations': request.user.reservation_set.order_by('timeslot__start_time')
    })

@login_required
@membership_required
def reservation_detail(request, reservation_id):
    reservation = request.user.reservation_set.get(pk=reservation_id)

    return render(request, 'timeslots/reservation_detail.html', {
        'reservation': reservation
    })

@login_required
@membership_required
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
