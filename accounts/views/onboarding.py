from django.shortcuts import render, redirect
from ..forms import PasswordChangeForm
from ..models import Invitation, User
from django.contrib import messages
from signup.models import Registration

def accept(request):

    if 'code' not in request.GET: raise Exception('Code parameter missing.')
    if Registration.objects.filter(uuid=request.GET['code']).exists():
        registration = Registration.objects.get(uuid=request.GET['code'])
        # TODO: Import membership info from membership system
        u = User.objects.import_member_from_billing_system(registration.membership_person_record)
        registration.user_id = u.id
        registration.save()
    else:
        raise Exception('Invalid Code')
    request.session['user_id'] = u.id
    return redirect('/accounts/onboard/password/')

    # messages.error(request, 'invalid code')
    # return render(request, 'accounts/onboarding/error.html', {})



    # TODO: Create Clubhouse account from membership data
    # TODO: Update Registration object with Account pkey
    # TODO: Save Registration object
    # TODO: Redirect to '/accounts/onboard/password'

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
