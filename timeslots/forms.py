from django import forms
from localflavor.us.forms import USStateField, USZipCodeField, USStateSelect
from localflavor.us.us_states import US_STATES
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError

from .models import Timeslot

class ReservationForm(forms.Form):
    knows_the_rules = forms.BooleanField(label="I have read the temporary rules and will do my best to be safe.")

class CancelReservationForm(forms.Form):
    confirmed = forms.CharField(widget=forms.HiddenInput())

class TimeslotForm(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ['is_closed_by_staff']
