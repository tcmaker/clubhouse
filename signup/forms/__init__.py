import os
from django import forms
from localflavor.us.forms import USStateField, USZipCodeField, USStateSelect
from localflavor.us.us_states import US_STATES
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from ..validators import validate_auth0_password

from membership.models import PaymentPlan, SIGNUP_PAYMENT_METHODS

class AccountForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_errors = True

    given_name = forms.CharField(
        label='First Name',
        max_length=100
    )

    family_name = forms.CharField(
        label='Last Name',
        max_length=100
    )

    email = forms.EmailField(label='Email')
    username = forms.CharField(
        label='Username',
        max_length=30,
        help_text='Some systems at Twin Cities Maker, like our Wiki software, require a username. Choose wisely &mdash; it will be very difficult to change this later! '
    )

    def clean(self):
        cleaned_data = super().clean()
        # TODO: verify that username is available

        # if 'password' in cleaned_data and 'password_confirmation' in cleaned_data:
        #     if not cleaned_data['password'] == cleaned_data['password_confirmation']:
        #         self.add_error('password_confirmation', 'Passwords must match')

        return cleaned_data

class ContactForm(forms.Form):
    address_street1 = forms.CharField(
        label='Address',
        max_length=90
    )
    address_street2 = forms.CharField(
        label='Address line 2',
        required=False
    )
    address_city = forms.CharField(
        label='City',
        max_length=90
    )
    address_state = USStateField(
        label="State",
        initial="MN",
        widget=USStateSelect(attrs={'class':'custom-select'})
    )
    address_zip = USZipCodeField(
        label='Zip Code'
    )

    phone_number = PhoneNumberField(
        label="Phone",
        region='US'
    )
    phone_can_receive_sms = forms.BooleanField(
        label='This phone can receive SMS messages.',
        required=False
    )

    emergency_contact_name = forms.CharField(
        label='Emergency Contact',
        max_length=90
    )
    emergency_contact_phone = PhoneNumberField(region='US')

class DuesForm(forms.Form):
    dues_plan = forms.ModelChoiceField(
        label="Dues Plan",
        queryset=PaymentPlan.objects.order_by('sort_priority').all(),
        empty_label=None
    )

    payment_method = forms.ChoiceField(
        label="Payment Method",
        choices=SIGNUP_PAYMENT_METHODS
    )

class StripeForm(forms.Form):
    STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
    stripe_token = forms.CharField(widget=forms.HiddenInput())

class LegalForm(forms.Form):
    waives_liability = forms.BooleanField(label="I agree.")

class InviteHouseholdForm(forms.Form):
    send_invite = forms.ChoiceField(
        label="Invite someone?",
        choices=[
            ('now', 'Do it now.'),
            ('later', 'Do it later.'),
        ]
    )

    given_name = forms.CharField(
        label='First Name',
        max_length=100
    )

    family_name = forms.CharField(
        label='Last Name',
        max_length=100
    )

    email = forms.EmailField(label='Email')

    def full_clean(self):
        if 'send_invite' in self.data and self.data['send_invite'] == 'later':
            return
        return super().full_clean()
