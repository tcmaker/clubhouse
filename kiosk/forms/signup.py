from django import forms
from localflavor.us.forms import USStateField, USZipCodeField, USStateSelect
from localflavor.us.us_states import US_STATES
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from ..rest_actions import dues_plans

# password validation
from django.contrib.auth import password_validation, get_user_model

class AccountForm(forms.Form):
    error_messages = {
        'password_mismatch': 'The two password fields didn’t match.',
        'username_unavailable': 'This username is not available.',
    }

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

    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput,
        help_text='Enter the same password as before, for verification.'
    )

    def clean_username(self):
        proposed = self.cleaned_data.get('username')
        if get_user_model().objects.filter(username=proposed).exists():
            raise forms.ValidationError(
                self.error_messages['username_unavailable'],
                code='username_unavailable',
            )
        return proposed

    def clean_password_confirmation(self):
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password_confirmation

    def _post_clean(self):
        super()._post_clean()

        password = self.cleaned_data.get('password_confirmation')

        if password:
            try:
                password_validation.validate_password(password)
            except forms.ValidationError as error:
                self.add_error('password_confirmation', error)

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
    dues_plan = forms.ChoiceField(
        label="Dues Plan",
        choices=dues_plans(),
    )

    # payment_method = forms.ChoiceField(
    #     label="Payment Method",
    #     choices=SIGNUP_PAYMENT_METHODS
    # )

class LegalForm(forms.Form):
    waives_liability = forms.BooleanField(label="I agree to the terms and conditions presented above.")
