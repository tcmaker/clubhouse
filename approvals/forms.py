from django import forms

class HouseholdApprovalForm(forms.Form):
    keyfob_code = forms.CharField(
        label='Keyfob Code',
        help_text="The code to the keyfob that you are issuing to the member"
    )

    def clean(self):
        super().clean()
