from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import urls
from kiosk.models import Signup
from .forms import HouseholdApprovalForm
from . import activation

from django.shortcuts import render

#### Signups ####

@login_required
def index(request):
    context = {
        'signups': Signup.pending_approval.all(),
    }
    return render(request, 'approvals/index.html', context)

# class PendingSignupList(ListView):
#     model = SignupProgress
#     context_object_name = 'signups'
class PendingSignupDetail(LoginRequiredMixin, DetailView):
    model = Signup
    template_name='approvals/signup_detail.html'
    context_object_name = 'signup'

class ApproveHouseholdForm(LoginRequiredMixin, FormView):
    template_name = 'approvals/approve_household.html'
    form_class = HouseholdApprovalForm

    def get(self, request, *args, **kwargs):
        progress = Signup.objects.get(pk=kwargs['pk'])
        self.initial = {
            'username': progress.data['person']['username'],
        }

        self.extra_context = {
            'signup': progress,
        }
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        # import code; code.interact(local=dict(globals(), **locals()))
        activation.approve_signup(Signup.objects.get(pk=int(self.kwargs['pk'])), form.cleaned_data['keyfob_code'])
        return HttpResponseRedirect(urls.reverse('approvals:approval_index'))

class RejectHouseholdForm(LoginRequiredMixin, FormView):
    template_name = 'approvals/approve_household.html'
    form_class = HouseholdApprovalForm
