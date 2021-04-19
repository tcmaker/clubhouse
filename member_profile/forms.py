from django import forms
from localflavor.us.forms import USStateField, USZipCodeField, USStateSelect
from localflavor.us.us_states import US_STATES
from phonenumber_field.formfields import PhoneNumberField
# from crispy_forms.helper import FormHelper

class AddressForm(forms.Form):
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

class BasicInfoForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
    email = forms.EmailField(label='Email')

class EmergencyContactForm(forms.Form):
    emergency_contact_name = forms.CharField(
        label='Emergency Contact',
        max_length=90
    )
    emergency_contact_phone = PhoneNumberField(region='US')

class PhoneForm(forms.Form):
    phone_number = PhoneNumberField(
        label="Phone",
        region='US'
    )
    phone_can_receive_sms = forms.BooleanField(
        label='This phone can receive SMS messages.',
        required=False
    )
