from django import forms

class SubscriptionForm(forms.Form):
    # price
    # recurring?
    pass

class StripeForm(forms.Form):
    stripe_token = forms.CharField(widget=forms.HiddenInput())

class SubscriptionForm(forms.Form):
    ONE_MONTH_PLAN = 'monthly'
    SIX_MONTH_PLAN = '6month'
    TWELVE_MONTH_PLAN = '12month'

    plan = forms.ChoiceField(choices={
        (ONE_MONTH_PLAN, 'Monthly Plan'),
        (SIX_MONTH_PLAN, 'Six Month Plan'),
        (TWELVE_MONTH_PLAN, 'Twelve Month Plan'),
    })

class InvoiceOrAutopayForm(forms.Form):
    AUTOPAY_BILLING = 'autopay'
    INVOICE_BILLING = 'invoice'

    payment_strategy = forms.ChoiceField(choices={
        (AUTOPAY_BILLING, 'Charge my credit card automatically'),
        (INVOICE_BILLING, 'Send me an invoice every month'),
    })


class EnrollForm(SubscriptionForm):
    pass

class AutoPayEnrollForm(EnrollForm):
    stripe_token = forms.CharField(widget=forms.HiddenInput())
