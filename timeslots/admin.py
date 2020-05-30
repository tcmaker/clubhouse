from django.contrib import admin
from .models import Reservation, Timeslot

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    date_hierarchy = 'timeslot__start_time'
    list_display = ('__str__', 'reservation_area', 'reservation_start_time', 'reservation_end_time', 'member')

    list_filter = ('timeslot__area',)

    def reservation_area(self, obj):
        return obj.timeslot.area.name

    def reservation_start_time(self, obj):
        return obj.timeslot.start_time

    def reservation_end_time(self, obj):
        return obj.timeslot.end_time


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_time'
    list_display = ('start_time', 'end_time', 'area', 'closure_status', 'reservation_count',)

    def closure_status(self, obj):
        if obj.is_closed_by_staff: return 'closed'
        return 'open'

    list_filter = ('area', 'is_closed_by_staff')

    ordering = ['start_time', 'area__name']
