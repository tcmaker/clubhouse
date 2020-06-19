from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.timezone import now as tz_now
from ..models import Registration
from .signup import SignupWizardView
from accounts.models import User
from dashboard import civicrm
from . import steps

# Forms
from ..forms import StripeForm
from accounts.forms import PasswordChangeForm

class OnboardingView(SignupWizardView):
    def next_uncompleted_step(self, session):
        registration = self.signup_progress(session)

        if not registration.account_created_at:
            return steps.ONBOARDING_PASSWORD_STEP

        if not invitation.contact_info_collected_at:
            return steps.ONBOARDING_DUES_STEP

        if not invitation.liability_waiver_accepted_at:
            return steps.ONBOARDING_FINAL_STEP

class PasswordCreationView(OnboardingView):
    view_template = 'signup/account.html'
    form_class = PasswordChangeForm
    current_step = steps.ONBOARDING_PASSWORD_STEP

    def success(self, request, form):
        registration = self.signup_progress(request.session)
        user = User.objects.import_member_by_contact_id(registration.civicrm_identifier)
        user.create_cognito_record_with_password(form.cleaned_data['password'])
        registration.user = user
        registration.account_created_at = tz_now()
        registration.save()

class DuesView(SignupWizardView):
    view_template = 'signup/dues_payment.html'
    form_class = StripeForm
    current_step = steps.PAYMENT_CARD_STEP

    def post(self, request):
        form = self.form_object(request.POST)
        if form.is_valid():
            registration = self.signup_progress(request.session)
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Update the customer source
            customer = stripe.Customer.retrieve(registration.stripe_identifier)
            customer.source = form.cleaned_data['stripe_token']
            customer.save()

            # Charge $55.00
            charge = stripe.Charge.create(
                customer = customer.id,
                amount = 5500, # $20.00 is 2,000 pennies
                currency = 'usd',
                description = 'First Month of Dues',
                receipt_email = registration.email
            )

            if charge.outcome.network_status == 'approved_by_network':
                registration.paid_setup_fee_at = tz_now()
                registration.save()
                return HttpResponseRedirect(django.urls.reverse('signup:' + self.next_uncompleted_step(request.session)))
            else:
                messages.error(request, 'Card payment failed. Please try again!');
        return render(request, self.view_template, {'form': form})

class DuesPaymentView()
    view_template = 'signup/dues.html'
    form_class = StripeForm

    def success(self, request, form):
        registration = self.signup_progress(request.session)

        membership_completed_at
