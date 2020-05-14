from django.contrib import admin
from .models import Reservation, Timeslot

admin.site.register(Reservation)
admin.site.register(Timeslot)
