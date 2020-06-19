from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from django import urls
from django.contrib import messages
from django.utils.timezone import now as tz_now
from signup.models import Registration
from .forms import KeyfobCodeForm, MembershipApprovalForm

class ApprovalMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = 'accounts.add_user'

class IndexView(ApprovalMixin, View):
    def get(self, request):
        registrations = {
            'pending_keyfobs': Registration.pending.pending_keyfobs,
            'pending_approval': Registration.pending.pending_approval,
        }

        return render(request, 'approvals/index.html', {
            'registrations': registrations,
        })

#### Registrations ####

class RegistrationIndexView(ApprovalMixin, RedirectView):
    pass

# Pending Keyfobs
class RegistrationPendingKeyfobList(ApprovalMixin, ListView):
    model = Registration
    queryset = Registration.pending.pending_keyfobs()
    template_name = 'approvals/registration_pending_keyfob_list.html'

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        print(ret)
        return ret

class RegistrationPendingKeyfobDetail(ApprovalMixin, DetailView):
    model = Registration
    queryset = Registration.pending.pending_keyfobs()
    template_name = 'approvals/registration_pending_keyfob_detail.html'

class RegistrationPendingKeyfobForm(ApprovalMixin, FormView):
    template_name = 'approvals/registration_pending_keyfob_form.html'
    form_class = KeyfobCodeForm

    def setup(self, request, *args, **kwargs):
        self.registration = Registration.pending.pending_keyfobs().get(pk=kwargs['pk'])
        self.extra_context = {
            'registration': self.registration,
        }
        return super().setup(request, *args, **kwargs)

    def form_valid(self, form):
        self.registration.keyfob_code = form.cleaned_data['keyfob_code']
        self.registration.save()
        self.registration.add_civicrm_keyfob_code()
        self.registration.keyfob_issued_at = tz_now()
        self.registration.save()
        return HttpResponseRedirect(urls.reverse('approvals:registration_pending_keyfob_list'))

# Pending Final Approval
class RegistrationPendingInviteList(ApprovalMixin, ListView):
    model = Registration
    queryset = Registration.pending.pending_approval()
    template_name = 'approvals/registration_pending_invite_list.html'

class RegistrationPendingInviteDetail(ApprovalMixin, DetailView):
    model = Registration
    queryset = Registration.pending.pending_approval()
    template_name = 'approvals/registration_pending_invite_detail.html'

class RegistrationPendingInviteForm(ApprovalMixin, FormView):
    template_name = 'approvals/registration_pending_invite_form.html'
    form_class = MembershipApprovalForm

    def setup(self, request, *args, **kwargs):
        self.registration = Registration.pending.pending_approval().get(pk=kwargs['pk'])
        self.extra_context = {
            'registration': self.registration,
        }
        return super().setup(request, *args, **kwargs)

    def form_valid(self, form):
        self.registration.send_invitation_email()
        self.registration.account_invitation_created_at = tz_now()
        self.registration.save()
        return HttpResponseRedirect(urls.reverse('approvals:registration_pending_keyfob_list'))
