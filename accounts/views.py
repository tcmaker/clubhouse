from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.contrib.auth import logout
from django.contrib import messages
#from . import rest_actions

from .forms import PasswordChangeForm

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
#from . import rest_actions
from django.utils.dateparse import parse_datetime
from mozilla_django_oidc.views import OIDCLogoutView as MozillaLogoutView

import os, datetime

from django.conf import settings

class OIDCLogoutView(MozillaLogoutView):
    def get(self, request):
        # import code; code.interact(local=dict(globals(), **locals()))
        return self.post(request)

def login(request):
    # import code; code.interact(local=dict(globals(), **locals()))
    if request.user.is_authenticated:
        return redirect('/dashboard')

    # Initialze the OIDC view
    return redirect('/oidc/authenticate')

@login_required
def index(request):
    # Membership has expired. Show renewal instructions
    if False:
        return render(request, 'accounts/index-expired.html', {})
    # Membership is current
    return render(request, 'accounts/index.html', {
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            if request.user.change_cognito_password(form.cleaned_data['password']):
                messages.success(request, 'Password Updated')
            else:
                messages.error(request, 'Due to a system error, your password could not be changed.')
            return redirect('/dashboard')
    else:
        form = PasswordChangeForm()
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
