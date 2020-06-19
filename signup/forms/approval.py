from django import forms

class HouseholdApprovalForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=30,
        help_text="Make sure this is the username they want. They might have to change it if it's already taken."
    )

    keyfob_code = forms.CharField(
        label='Keyfob Code',
        help_text="The code to the keyfob that you are issuing to the member"
    )

    def clean(self):
        super().clean()

class InvitationApprovalForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=30,
        help_text="Make sure this is the username they want. They might have to change it if it's already taken."
    )

    keyfob_code = forms.CharField(
        label='Keyfob Code',
        help_text="The code to the keyfob that you are issuing to the member"
    )
