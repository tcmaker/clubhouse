from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.timezone import now as tz_now
from ..forms import AccountForm, ContactForm, LegalForm
from ..models import Invitation
from .signup import SignupWizardView
from . import steps

import django.urls

def accept_invite(request, code=None):
    try:
        invitation = Invitation.objects.get(uuid=code)
    except:
        return HttpResponseRedirect('https://tcmaker.org/')

    invitation.accepted_at = tz_now()
    invitation.save()
    request.session['invitation_id'] = invitation.id
    return HttpResponseRedirect(django.urls.reverse('signup:' + steps.INVITE_ACCOUNT_INFO_STEP))

def invite_final(request):
    request.session.flush()
    return render(request, 'signup/final.html', {})

class InviteWizardView(SignupWizardView):
    def invitation(self, session):
        return Invitation.objects.get(id=session['invitation_id'])

    def next_uncompleted_step(self, session):
        invitation = self.invitation(session)

        if not invitation.basic_info_collected_at:
            return steps.INVITE_ACCOUNT_INFO_STEP

        if not invitation.contact_info_collected_at:
            return steps.INVITE_CONTACT_INFO_STEP

        if not invitation.liability_waiver_accepted_at:
            return steps.INVITE_LEGAL_STEP

        return steps.INVITE_FINAL_STEP

class InviteAccountView(InviteWizardView):
    view_template = 'signup/account.html'
    form_class = AccountForm
    current_step = steps.INVITE_ACCOUNT_INFO_STEP

    def success(self, request, form):
        progress = self.invitation(request.session)
        progress.add_form_data(form.cleaned_data)
        progress.basic_info_collected_at = tz_now()
        progress.save()

class InviteContactView(InviteWizardView):
    view_template = 'signup/contact.html'
    form_class = ContactForm
    current_step = steps.INVITE_CONTACT_INFO_STEP

    def success(self, request, form):
        progress = self.invitation(request.session)
        progress.add_form_data(form.cleaned_data)
        progress.contact_info_collected_at = tz_now()
        progress.save()

class InviteLegalView(InviteWizardView):
    view_template = 'signup/legal.html'
    form_class = LegalForm
    current_step = steps.INVITE_LEGAL_STEP

    def success(self, request, form):
        progress = self.invitation(request.session)
        progress.add_form_data(form.cleaned_data)
        progress.liability_waiver_accepted_at = tz_now()
        progress.save()
