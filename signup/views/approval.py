from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import urls
from ..models import Registration
from .forms import approval
from . import activation

from django.shortcuts import render

#### Signups ####

@login_required
def index(request):
    context = {
        'signups': Registration.pending_approval.all(),
        'invitations': Invitation.pending_approval.filter(membership_id__isnull=False),
    }
    return render(request, 'signup/approval/index.html', context)

# class PendingSignupList(ListView):
#     model = Registration
#     context_object_name = 'signups'
class PendingSignupDetail(LoginRequiredMixin, DetailView):
    model = Registration
    context_object_name = 'signup'

class ApproveHouseholdForm(LoginRequiredMixin, FormView):
    template_name = 'signup/approval/approve_household.html'
    form_class = approval.HouseholdApprovalForm

    def get(self, request, *args, **kwargs):
        progress = Registration.objects.get(pk=kwargs['pk'])
        self.initial = {
            'username': progress.data['username'],
        }

        self.extra_context = {
            'signup': progress,
        }
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        # import code; code.interact(local=dict(globals(), **locals()))
        activation.approve_household(Registration.objects.get(pk=int(self.kwargs['pk'])))
        return HttpResponseRedirect(urls.reverse('signup:approval_index'))

class RejectHouseholdForm(LoginRequiredMixin, FormView):
    template_name = 'signup/approval/approve_household.html'
    form_class = approval.HouseholdApprovalForm

#### Invitations ####

# class PendingInvitationList(ListView):
#     pass

class PendingInvitationDetail(LoginRequiredMixin, DetailView):
    model = Invitation
    context_object_name = 'invite'

class PendingInvitationForm(LoginRequiredMixin, FormView):
    template_name = 'signup/approval/approve_invite.html'
    form_class = approval.InvitationApprovalForm

    def get(self, request, *args, **kwargs):
        invitation = Invitation.objects.get(pk=kwargs['pk'])
        self.initial = {
            'username': invitation.data['username'],
        }

        self.extra_context = {
            'invite': invitation,
        }
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        # import code; code.interact(local=dict(globals(), **locals()))
        activation.approve_invitation(Invitation.objects.get(pk=int(self.kwargs['pk'])))
        return HttpResponseRedirect(urls.reverse('signup:approval_index'))
