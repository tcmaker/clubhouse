from django.contrib import admin
from .models import Reservation, Timeslot

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    date_hierarchy = 'timeslot__start_time'
    list_display = ('__str__', 'reservation_area', 'reservation_start_time', 'reservation_end_time', 'member')

    def reservation_area(self, obj):
        return obj.timeslot.area.name

    def reservation_start_time(self, obj):
        return obj.timeslot.start_time

    def reservation_end_time(self, obj):
        return obj.timeslot.end_time

@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_time'
    list_display = ('start_time', 'end_time', 'area', 'is_closed_by_staff', 'reservation_count')

    ordering = ['start_time', 'area__name']

    # search_fields = ['last_name', 'first_name', 'email', 'username']
    #
    #
    #
    # fieldsets = (
    #     ('Basic Information', {
    #         'fields': ('last_name', 'first_name', 'email'),
    #     }),
    #
    #     ('Account Information', {
    #         'fields': ('username', 'sub'),
    #     }),
    #
    #     ('Integrations', {
    #         'fields': ('civicrm_identifier', 'civicrm_keyfob_code'),
    #     }),
    #
    #     ('Advanced', {
    #         'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
    #     })
    # )
