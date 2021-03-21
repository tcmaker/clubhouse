from django import forms
from localflavor.us.forms import USStateField, USZipCodeField, USStateSelect
from localflavor.us.us_states import US_STATES
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError

from tempus_dominus.widgets import DateTimePicker
from django.contrib.admin.widgets import AdminDateWidget

from .models import Timeslot

# We have to extend Tempus Dominus to fix a bug
class MyDateTimePicker(DateTimePicker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.js_options['icons']['time'] = "fas fa-clock"

class ReservationForm(forms.Form):
    knows_the_rules = forms.BooleanField(label="I have read the temporary rules and will do my best to be safe.")

class CancelReservationForm(forms.Form):
    confirmed = forms.CharField(widget=forms.HiddenInput())

class TimeslotForm(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ['is_closed_by_staff']

class CloseTimeslotRangeForm(forms.Form):
    desired_state = forms.ChoiceField(label="Action to Perform", choices=(
        ('close', 'Close Timeslots'),
        ('open', 'Open Timeslots'),
    ))


    start_time = forms.DateTimeField(widget=MyDateTimePicker(
        options={
            'useCurrent': True,
            'collapse': True,
        },

        attrs={
            'append': 'fa fa-calendar',
            'icon_toggle': True,
            'input_group': True,
        }
    ))
    end_time = forms.DateTimeField(widget=MyDateTimePicker(
        options={
            'useCurrent': True,
            'collapse': True,
        },
        attrs={
            'append': 'fa fa-calendar',
            'icon_toggle': True,
        }
    ))
