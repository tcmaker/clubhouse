from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.contrib.auth import logout
from django.contrib import messages
from django.http import Http404, HttpResponse
from .civicrm import get_member_info
from .models import User
import json
#from . import rest_actions

from .forms import PasswordChangeForm, CiviCRMContactImportForm, CognitoAdminForm

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

@login_required
def import_civicrm_user(request):
    if request.method == 'POST':
        form = CiviCRMImportForm(request.POST)
        if form.is_valid():
            try:
                u = import_member_by_contact_id(contact_id)
                u.sync_membership_status()

                if form.cleaned_data['create_sso_account_and_invite']:
                    u.create_cognito_record(True) # If the data is already in CiviCRM, we assume the email has been verified.

                return redirect('/admin/accounts/user/' + str(u.id))
            except Exception as e:
                messages.error(request, e)
                return redirect('/admin/accounts/user/') # TODO Figure out URL name for this path


#### Admin Views ####
@login_required
@permission_required('accounts.add_user')
def import_civicrm_contact(request):
    if request.method == 'POST':
        form = CiviCRMContactImportForm(request.POST)
        if form.is_valid():
            try:
                u = User.objects.import_member_by_contact_id(form.cleaned_data['contact_id'])
                u.sync_membership_info()
                u.sync_membership_status()

                if form.cleaned_data['create_sso_account_and_invite']:
                    u.create_cognito_record(True) # If the data is already in CiviCRM, we assume the email has been verified.

                return redirect('/admin/accounts/user/' + str(u.id))
            except Exception as e:
                messages.error(request, e)
                return redirect('/admin/accounts/user/') # TODO Figure out URL name for this path
        else:
            print(form.__dict__)
    else:
        form = CiviCRMContactImportForm()

    return render(request, 'admin/accounts/user/import_form.html', {
        'form': form,
    })

@login_required
@permission_required('accounts.add_user')
def import_civicrm_contact_preview(request):
    payload = {}
    contact_id = request.GET.get('contact_id', False)
    if contact_id:
        try:
            resp = get_member_info(contact_id)
            for key in ['contact_id', 'contact_type', 'first_name', 'last_name', 'email']:
                payload[key] = resp[key]
        except:
            raise Http404

    payload = json.dumps(payload)
    return HttpResponse(payload, content_type = 'application/json')

@login_required
@permission_required('accounts.add_user')
def cognito_admin(request, pk):
    user = User.objects.get(pk=pk)
    cognito_record = user.get_cognito_record()

    if request.method == 'POST':
        form = CognitoAdminForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['cognito_action']
            try:
                if action == 'create_account': user.create_cognito_record(True)
                if action == 'reset_temporary_password': user.cognito_reset_temporary_password()
                redirect(request, 'admin/accounts/user/%s/change/' % user.id)
            except Exception as e:
                messages.error(request, e)
    else:
        if cognito_record is not None:
            initial_vals = {'cognito_action': 'reset_temporary_password'}
        else:
            initial_vals = {'cognito_action': 'create_account'}
        form = CognitoAdminForm(initial_vals)

    return render(request, 'admin/accounts/user/cognito_form.html', {
        'form': form,
        'user': user,
        'cognito_record': cognito_record,
    })
