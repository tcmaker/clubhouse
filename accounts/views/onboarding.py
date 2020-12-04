from django.shortcuts import render, redirect
from ..forms import PasswordChangeForm
from ..models import Invitation, User
from django.contrib import messages
from signup.models import Registration

from .. import civicrm

def accept(request):
    try:
        if 'code' not in request.GET: raise Exception('Code parameter missing.')
        # Search for an onboarding email
        invitation = None
        if Invitation.objects.filter(uuid=request.GET['code']).exists():
            invitation = Invitation.objects.get(uuid=request.GET['code'])
        elif Registration.objects.filter(uuid=request.GET['code']).exists():
            invitation = Registration.objects.get(uuid=request.GET['code'])
            u = User.objects.import_member_by_contact_id(invitation.civicrm_identifier)
            invitation.user_id = u.id
            invitation.save()
        else:
            raise Exception('Invalid Code')
        request.session['user_id'] = invitation.user.id
        return redirect('/accounts/onboard/password/')
    except ValueError as e:
        messages.error(request, 'invalid code')
        return render(request, 'accounts/onboarding/error.html', {})

def set_password(request):
    if 'user_id' not in request.session:
        return render(request, 'accounts/onboarding/error.html', {})

    user = User.objects.get(pk=request.session['user_id'])

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            resp = user.create_cognito_record_with_password(form.cleaned_data['password'])
            if user.sub is not None:
                return redirect('/accounts/onboard/instructions/')
            else:
                return render(request, 'accounts/onboarding/error.html', {})
    else:
        form = PasswordChangeForm()
    return render(request, 'accounts/onboarding/set_password.html', {
        'form': form
    })

def instructions(request):
    if 'user_id' not in request.session:
        return render(request, 'accounts/onboarding/error.html', {})
    return render(request, 'accounts/onboarding/instructions.html', {
        'user': User.objects.get(pk=request.session['user_id'])
    })
