from django import forms
from crispy_forms.helper import FormHelper
from django.contrib.auth import password_validation

class PasswordChangeForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html()
    )

    password_confirmation = forms.CharField(
        widget=forms.PasswordInput,
        help_text='Enter the same password as before, for verification.'
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except forms.ValidationError as error:
                self.add_error('password', error)
        return password

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
        ret = super()._post_clean()

        password = self.cleaned_data.get('password_confirmation')

        if password:
            try:
                password_validation.validate_password(password)
            except forms.ValidationError as error:
                self.add_error('password_confirmation', error)

        return ret

class CiviCRMContactImportForm(forms.Form):
    contact_id = forms.IntegerField(help_text='CiviCRM Contact ID', required=True)
    create_sso_account_and_invite = forms.BooleanField(
        help_text='Create SSO account and invite to dashboard', default=True, required=False
    )

class CognitoAdminForm(forms.Form):
    cognito_action = forms.CharField(widget=forms.HiddenInput())
