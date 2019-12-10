from django import forms
from . import rest_actions
import stripe, os

class DuesForm(forms.Form):
    STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
    stripe_token = forms.CharField(widget=forms.HiddenInput())
    dues_plan = forms.ChoiceField(
        label="Dues Plan",
        choices=rest_actions.dues_plans,
    )
