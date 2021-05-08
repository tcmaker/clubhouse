from django import forms

quantities = [
    ('1', '1 hour'),
    ('2', '2 hours'),
    ('3', '3 hours'),
    ('4', '4 hours'),
    ('5', '5 hours'),
    ('6', '6 hours'),
    ('7', '7 hours'),
    ('8', '8 hours'),
]

class HourlyForm(forms.Form):
    quantity = forms.ChoiceField(choices=quantities)

class AddToCartForm(forms.Form):
    product_id = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.ChoiceField(choices=quantities)
