from django.shortcuts import render, redirect
from .forms import BasicInfoForm, AddressForm, PhoneForm, EmergencyContactForm

from accounts.auth.decorators import membership_required
from django.contrib.auth.decorators import login_required

from dashboard import civicrm
from billing.util import api_get, api_patch

@login_required
@membership_required
def index(request):
    profile = api_get(request.user.membership_person_record)

    return render(request, 'member_profile/index.html', context={
        'profile': profile,
    })

@login_required
@membership_required
def email_confirm_notice(request):
    return render(request, 'member_profile/email_confirm_notice.html', context={})

@login_required
@membership_required
def basic_info_form(request):
    if request.method == 'POST':
        form = BasicInfoForm(request.POST)
        if form.is_valid():
            # request.user.first_name = form.cleaned_data['first_name']
            # request.user.last_name = form.cleaned_data['last_name']
            api_patch(request.user.membership_person_record, {
                'given_name': form.cleaned_data['first_name'],
                'family_name': form.cleaned_data['last_name']
            })

            request.user.sync_membership_info()
            request.user.sync_cognito_user_attributes()

            if request.user.email != form.cleaned_data['email']:
                # Change email
                request.user.set_pending_email_and_verify(form.cleaned_data['email'])
                return redirect('/profile/email-confirm-notice/')
            return redirect('/profile')
    else:
        form = BasicInfoForm({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    return render(request, 'member_profile/basic_info_form.html', context={
        'form': form
    })

@login_required
@membership_required
def address_form(request):
    address_record = civicrm.profile_get_address(request.user.civicrm_identifier)

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address_properties = {
                'address_street1': form.cleaned_data['address_street1'],
                'address_street2': form.cleaned_data['address_street2'],
                'address_city': form.cleaned_data['address_city'],
                'address_zip': form.cleaned_data['address_zip'],
                'address_state': form.cleaned_data['address_state'],
            }

            api_patch(request.user.membership_person_record, address_properties)

            return redirect('/profile/')
    else:
        person = api_get(request.user.membership_person_record)
        address_fields = person

        form = AddressForm(address_fields)

    return render(request, 'member_profile/basic_info_form.html', context={
        'form': form
    })

@login_required
@membership_required
def phone_form(request):
    try:
        phone = civicrm.profile_get_phone(request.user.civicrm_identifier)
    except:
        phone = {
            'phone': None,
            'phone_type_id': 1,
        }

    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            civicrm.profile_update_phone(
                request.user.civicrm_identifier,
                phone['id'],
                form.cleaned_data['phone_number'],
                form.cleaned_data['phone_can_receive_sms']
            )
            print('redirect')
            return redirect('/profile/')
    else:
        can_receive_sms = int(phone['phone_type_id']) == 2
        form = PhoneForm({
            'phone_number': phone['phone'],
            'phone_can_receive_sms': can_receive_sms
        })

    return render(request, 'member_profile/basic_info_form.html', context={
        'form': form
    })

@login_required
@membership_required
def emergency_contact_form(request):
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            api_patch(request.user.membership_person_record, json={
                'emergency_contact_name': form.cleaned_data['emergency_contact_name'],
                'emergency_contact_phone': str(form.cleaned_data['emergency_contact_phone']),
            })
            return redirect('/profile/')
    else:
        person = api_get(request.user.membership_person_record)
        form = EmergencyContactForm({
            'emergency_contact_name': person['emergency_contact_name'],
            'emergency_contact_phone': person['emergency_contact_phone'],
        })

    return render(request, 'member_profile/basic_info_form.html', context={
        'form': form
    })
