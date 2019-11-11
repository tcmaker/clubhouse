from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.timezone import now as tz_now
from ..forms import AccountForm, ContactForm, DuesForm, StripeForm, LegalForm, InviteHouseholdForm
from ..models import SignupProgress, Invitation
from . import steps

import django.urls
import stripe
import os

def index(request):
    return render(request, 'signup/index.html', {})

def final(request):
    request.session.flush()
    return render(request, 'signup/final.html', {})

class SignupWizardView(View):
    # TODO: use `abc` module to mark these properties abstract
    view_template = None
    form_class = None
    current_step = None

    # TODO: use `abc` module to mark this method abstract
    def success(self, request, form):
        pass

    def get(self, request):
        next_step = self.next_uncompleted_step(request.session)

        if next_step != self.current_step:
            return HttpResponseRedirect(django.urls.reverse('signup:' + next_step))

        return render(request, self.view_template, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        # import code; code.interact(local=dict(globals(), **locals()))
        if form.is_valid():
            self.success(request, form)
            return HttpResponseRedirect(django.urls.reverse('signup:' + self.next_uncompleted_step(request.session)))
        return render(request, self.view_template, {'form': form})

    def signup_progress(self, session):
        if 'progress_id' in session:
            progress = SignupProgress.objects.get(id=session['progress_id'])
        else:
            progress = SignupProgress.objects.create(data={})
            session['progress_id'] = progress.id
        return progress

    def next_uncompleted_step(self, session):
        progress = self.signup_progress(session)

        if not progress.basic_info_collected_at:
            return steps.ACCOUNT_INFO_STEP

        if not progress.contact_info_collected_at:
            return steps.CONTACT_INFO_STEP

        if not progress.payment_plan_collected_at:
            return steps.DUES_INFO_STEP

        if not progress.payment_info_collected_at:
            d = {
                'card': steps.PAYMENT_CARD_STEP,
                'paypal': steps.PAYMENT_PAYPAL_STEP,
                'ach': steps.PAYMENT_ACH_STEP,
                'offline': steps.PAYMENT_CASH_STEP,
            }
            return d[progress.data['payment_method']]

        if not progress.liability_waiver_accepted_at:
            return steps.LEGAL_STEP

        if not progress.invitation_screen_passed_at:
            return steps.INVITE_STEP

        # All checkpoints cleared
        return steps.DONE_STEP

### Concrete View Classes ###

class AccountView(SignupWizardView):
    view_template = 'signup/account.html'
    form_class = AccountForm
    current_step = steps.ACCOUNT_INFO_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data(form.cleaned_data)
        progress.basic_info_collected_at = tz_now()
        progress.save()

class ContactView(SignupWizardView):
    view_template = 'signup/contact.html'
    form_class = ContactForm
    current_step = steps.CONTACT_INFO_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data(form.cleaned_data)
        progress.contact_info_collected_at = tz_now()
        progress.save()

class DuesView(SignupWizardView):
    view_template = 'signup/dues.html'
    form_class = DuesForm
    current_step = steps.DUES_INFO_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data(form.cleaned_data)
        progress.data['payment_plan_id'] = form.cleaned_data['dues_plan'].id
        progress.payment_plan_collected_at = tz_now()
        progress.save()

# Abstract class
class StripeView(SignupWizardView):
    form_class = StripeForm

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        stripe.api_key = os.environ['STRIPE_SECRET_KEY']
        customer = stripe.Customer.create(
            name = ', '.join([
                progress.data['family_name'],
                progress.data['given_name']
            ]),
            email = progress.data['email']
        )
        customer.source = form.cleaned_data['stripe_token']
        customer.save()
        progress.data['stripe_customer_identifier'] = customer.id
        progress.payment_info_collected_at = tz_now()
        progress.save()

class CardView(StripeView):
    view_template = 'signup/card.html'
    current_step = steps.PAYMENT_CARD_STEP

class ACHView(StripeView):
    view_template = 'signup/ach.html'
    current_step = steps.PAYMENT_ACH_STEP

class BraintreeView(SignupWizardView):
    view_template = 'signup/contact.html'
    form_class = ContactForm

    def success(self, request, form):
        pass

class LiabilityWaiverView(SignupWizardView):
    view_template = 'signup/legal.html'
    form_class = LegalForm
    current_step = steps.LEGAL_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data(form.cleaned_data)
        progress.liability_waiver_accepted_at = tz_now()
        progress.save()

class InvitationView(SignupWizardView):
    view_template = 'signup/invite.html'
    form_class = InviteHouseholdForm
    current_step = steps.INVITE_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        # `form.cleaned_data` might not exist, so we read from `form.data` instead.
        if form.data['send_invite'] == 'now':
            invitation = Invitation()
            invitation.given_name = form.cleaned_data['given_name']
            invitation.family_name = form.cleaned_data['family_name']
            invitation.email = form.cleaned_data['email']
            invitation.signup_progress = progress
            invitation.add_form_data(form.cleaned_data)
            invitation.save()

        progress.invitation_screen_passed_at = tz_now()
        progress.save()
