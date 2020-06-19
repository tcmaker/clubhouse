from django import forms

class KeyfobCodeForm(forms.Form):
    keyfob_code = forms.CharField(
        label='Keyfob Code',
        help_text="All leading zeros will be stripped from the keyfob code."
    )

class MembershipApprovalForm(forms.Form):
    activate_membership = forms.BooleanField(
        label='This person attended orientation and is ready to join.'
    )
