from django.urls import path
from .views import signup, steps

app_name = 'signup'

urlpatterns = [
    # New Signups
    path('', signup.index, name='index'),
    path('renew/', signup.renew, name='renew'),
    path('account/', signup.AccountView.as_view(), name=steps.ACCOUNT_INFO_STEP),
    path('contact/', signup.ContactView.as_view(), name=steps.CONTACT_INFO_STEP),
    path('setup-fee/', signup.SetupFeeView.as_view(), name=steps.PAYMENT_CARD_STEP),
    path('legal/', signup.LiabilityWaiverView.as_view(), name=steps.LEGAL_STEP),
    path('final/', signup.final, name=steps.DONE_STEP),
]
