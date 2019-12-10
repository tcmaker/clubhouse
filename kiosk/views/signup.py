from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.timezone import now as tz_now
from django.contrib.auth import get_user_model
from ..forms.signup import AccountForm, ContactForm, DuesForm, LegalForm
from . import steps
from ..models import Signup

import django.urls

def index(request):
    return render(request, 'kiosk/index.html', {})

def final(request):
    request.session.flush()
    return render(request, 'kiosk/final.html', {})

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
            return HttpResponseRedirect(django.urls.reverse('kiosk:' + next_step))

        return render(request, self.view_template, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        # import code; code.interact(local=dict(globals(), **locals()))
        if form.is_valid():
            self.success(request, form)
            return HttpResponseRedirect(django.urls.reverse('kiosk:' + self.next_uncompleted_step(request.session)))
        return render(request, self.view_template, {'form': form})

    def signup_progress(self, session):
        # import code; code.interact(local=dict(globals(), **locals()))
        if 'progress_id' in session:
            progress = Signup.objects.get(id=session['progress_id'])
        else:
            progress = Signup.objects.create(data={})
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

        if not progress.liability_waiver_accepted_at:
            return steps.LEGAL_STEP

        # All checkpoints cleared
        return steps.DONE_STEP

class AccountView(SignupWizardView):
    view_template = 'kiosk/account.html'
    form_class = AccountForm
    current_step = steps.ACCOUNT_INFO_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data('person', form.cleaned_data)

        # Create account on dashboard
        user = get_user_model()(
            first_name = form.cleaned_data['given_name'],
            last_name = form.cleaned_data['family_name'],
            email = form.cleaned_data['email'],
            username = form.cleaned_data['username']
        )
        user.set_password(form.cleaned_data['password'])
        user.save()

        progress.basic_info_collected_at = tz_now()
        progress.save()

class ContactView(SignupWizardView):
    view_template = 'kiosk/contact.html'
    form_class = ContactForm
    current_step = steps.CONTACT_INFO_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data('person', form.cleaned_data)
        progress.contact_info_collected_at = tz_now()

        # TODO: Create `Person` resource in membership system

        progress.save()

class DuesView(SignupWizardView):
    view_template = 'kiosk/dues.html'
    form_class = DuesForm
    current_step = steps.DUES_INFO_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data('dues', form.cleaned_data)
        progress.payment_plan_collected_at = tz_now()
        progress.save()

class LiabilityWaiverView(SignupWizardView):
    view_template = 'kiosk/legal.html'
    form_class = LegalForm
    current_step = steps.LEGAL_STEP

    def success(self, request, form):
        progress = self.signup_progress(request.session)
        progress.add_form_data('legal', form.cleaned_data)
        progress.liability_waiver_accepted_at = tz_now()
        progress.save()
