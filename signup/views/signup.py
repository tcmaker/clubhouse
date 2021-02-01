from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.views import View
from django.utils.timezone import now as tz_now
from ..forms import AccountForm, ContactForm, StripeForm, LegalForm, InviteHouseholdForm
from ..models import Registration
from . import steps


from django.conf import settings

import django.urls
import stripe
import os
import uuid

def index(request):
    request.session.flush()
    return render(request, 'signup/index.html', {})

def final(request):
    request.session.flush()
    return render(request, 'signup/final.html', {})

def renew(request):
    return render(request, 'signup/renew.html', {})

class SignupWizardView(View):
    # TODO: use `abc` module to mark these properties abstract
    view_template = None
    form_class = None
    current_step = None

    def form_object(self, raw_input=None):
        if raw_input is not None: return self.form_class(raw_input)
        return self.form_class()


    # TODO: use `abc` module to mark this method abstract
    def success(self, request, form):
        pass

    def get(self, request):
        next_step = self.next_uncompleted_step(request.session)

        if next_step != self.current_step:
            return HttpResponseRedirect(django.urls.reverse('signup:' + next_step))

        return render(request, self.view_template, {'form': self.form_object()})

    def post(self, request):
        form = self.form_object(request.POST)
        # import code; code.interact(local=dict(globals(), **locals()))
        if form.is_valid():
            self.success(request, form)
            return HttpResponseRedirect(django.urls.reverse('signup:' + self.next_uncompleted_step(request.session)))
        return render(request, self.view_template, {'form': form})

    def signup_progress(self, session):
        if 'progress_id' in session:
            progress = Registration.objects.get(id=session['progress_id'])
        else:
            progress = Registration.objects.create()
            session['progress_id'] = progress.id
        return progress

    def next_uncompleted_step(self, session):
        progress = self.signup_progress(session)

        if not progress.basic_info_collected_at:
            return steps.ACCOUNT_INFO_STEP

        if not progress.contact_info_collected_at:
            return steps.CONTACT_INFO_STEP

        if not progress.paid_setup_fee_at:
            return steps.PAYMENT_CARD_STEP

        if not progress.liability_waiver_accepted_at:
            return steps.LEGAL_STEP

        # All checkpoints cleared
        return steps.DONE_STEP

### Concrete View Classes ###

class AccountView(SignupWizardView):
    view_template = 'signup/account.html'
    form_class = AccountForm
    current_step = steps.ACCOUNT_INFO_STEP

    def success(self, request, form):
        registration = self.signup_progress(request.session)
        registration.given_name = form.cleaned_data['given_name']
        registration.family_name = form.cleaned_data['family_name']
        registration.email = form.cleaned_data['email']
        registration.basic_info_collected_at = tz_now()
        registration.save()

        # Update CiviCRM
        registration.create_civicrm_contact()

class ContactView(SignupWizardView):
    view_template = 'signup/contact.html'
    form_class = ContactForm
    current_step = steps.CONTACT_INFO_STEP

    def success(self, request, form):
        registration = self.signup_progress(request.session)
        registration.address_street1 = form.cleaned_data['address_street1']
        registration.address_street2 = form.cleaned_data['address_street2']
        registration.address_city = form.cleaned_data['address_city']
        registration.address_state = form.cleaned_data['address_state']
        registration.address_zip = form.cleaned_data['address_zip']
        registration.phone_number = form.cleaned_data['phone_number']
        registration.phone_can_receive_sms = form.cleaned_data['phone_can_receive_sms']
        registration.emergency_contact_name = form.cleaned_data['emergency_contact_name']
        registration.emergency_contact_phone = form.cleaned_data['emergency_contact_phone']
        registration.contact_info_collected_at = tz_now()
        registration.save()

        # Update CiviCRM
        registration.add_civicrm_address()
        registration.add_civicrm_phone()
        registration.add_civicrm_emergency_info()

class SetupFeeView(SignupWizardView):
    view_template = 'signup/card.html'
    form_class = StripeForm
    current_step = steps.PAYMENT_CARD_STEP

    def get(self, request):
        registration = self.signup_progress(request.session)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # If payment failed, the customer identifier will already exist.
        # Don't create one if you don't have to.
        if not registration.stripe_identifier:
            customer = stripe.Customer.create(
                name = ', '.join([
                    registration.family_name,
                    registration.given_name,
                ]),
                email = registration.email
            )
            registration.stripe_identifier = customer.id
            registration.save()

        # https://stripe.com/docs/api/idempotent_requests
        if 'stripe-idempotency-key' not in request.session:
            print("setting idempotency key")
            request.session['stripe-idempotency-key'] = str(uuid.uuid4())
        else:
            print("Found idempotency key: %s" % request.session['stripe-idempotency-key'])

        return super().get(request)

    def post(self, request):
        form = self.form_object(request.POST)
        if form.is_valid():
            registration = self.signup_progress(request.session)
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Update the customer source
            customer = stripe.Customer.retrieve(registration.stripe_identifier)
            customer.source = form.cleaned_data['stripe_token']
            customer.save()

            import code; code.interact(local=dict(globals(), **locals()))

            # Charge $20.00
            charge = stripe.Charge.create(
                customer = customer.id,
                amount = 2000, # $20.00 is 2,000 pennies
                currency = 'usd',
                description = 'One-time Setup Fee',
                receipt_email = registration.email,
                # https://stripe.com/docs/api/idempotent_requests
                idempotency_key = request.session['stripe-idempotency-key']
            )

            if charge.outcome.network_status == 'approved_by_network':
                registration.paid_setup_fee_at = tz_now()
                registration.save()
                return HttpResponseRedirect(django.urls.reverse('signup:' + self.next_uncompleted_step(request.session)))
            else:
                messages.error(request, 'Card payment failed. Please try again!');
        return render(request, self.view_template, {'form': form})

class LiabilityWaiverView(SignupWizardView):
    view_template = 'signup/legal.html'
    form_class = LegalForm
    current_step = steps.LEGAL_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.liability_waiver_accepted_at = tz_now()
        progress.save()
        progress.civicrm_accept_liability_waiver()
        progress.application_completed_at = tz_now()
        progress.save()
