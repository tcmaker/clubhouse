from django.shortcuts import render, redirect
from .forms import BasicInfoForm, AddressForm, PhoneForm, EmergencyContactForm

from dashboard import civicrm

def index(request):
    address = civicrm.profile_get_address(request.user.civicrm_identifier)
    phone = civicrm.profile_get_phone(request.user.civicrm_identifier)
    if 'state_province_id' in address:
        state_province = civicrm.profile_get_state_province(address['state_province_id'])
        state_province_abbreviation = state_province['abbreviation']
    else:
        state_province_abbreviation = 'MN'

    emergency_contact_info = {
        'name': civicrm.profile_get_emergency_contact_name(request.user.civicrm_identifier),
        'phone': civicrm.profile_get_emergency_contact_phone(request.user.civicrm_identifier),
    }

    return render(request, 'member_profile/index.html', context={
        'address':address,
        'phone': phone,
        'state_province_abbreviation': state_province_abbreviation,
        'emergency_contact_info': emergency_contact_info
    })

def email_confirm_notice(request):
    return render(request, 'member_profile/email_confirm_notice.html', context={})

def basic_info_form(request):
    if request.method == 'POST':
        form = BasicInfoForm(request.POST)
        if form.is_valid():
            # request.user.first_name = form.cleaned_data['first_name']
            # request.user.last_name = form.cleaned_data['last_name']
            civicrm.profile_update_name(
                request.user.civicrm_identifier,
                form.cleaned_data['first_name'],
                form.cleaned_data['last_name']
            )
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

def address_form(request):
    address_record = civicrm.profile_get_address(request.user.civicrm_identifier)

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address_properties = {
                'street_address': form.cleaned_data['address_street1'],
                'supplemental_address_1': form.cleaned_data['address_street2'],
                'city': form.cleaned_data['address_city'],
                'postal_code': form.cleaned_data['address_zip'],
                'state_province_id': form.cleaned_data['address_state'],
            }

            civicrm.profile_update_address(
                request.user.civicrm_identifier,
                address_record['id'],
                address_properties
            )
            return redirect('/profile/')
    else:
        if 'state_province_id' in address_record:
            state_province_abbreviation = civicrm.profile_get_state_province(address_record['state_province_id'])['abbreviation']
        else:
            state_province_abbreviation = 'MN'
        print(address_record)

        address_fields = {
            'address_street1': address_record['street_address'],
            'address_city': address_record['city'],
            'address_state': state_province_abbreviation,
            'address_zip': address_record['postal_code'],
        }
        if 'supplemental_address_1' in address_record:
            address_fields['address_street2'] = address_record['supplemental_address_1']

        form = AddressForm(address_fields)

    return render(request, 'member_profile/basic_info_form.html', context={
        'form': form
    })

def phone_form(request):
    phone = civicrm.profile_get_phone(request.user.civicrm_identifier)
    print(phone)

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

def emergency_contact_form(request):
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            civicrm.profile_update_emergency_contact(
                request.user.civicrm_identifier,
                form.cleaned_data['emergency_contact_name'],
                form.cleaned_data['emergency_contact_phone']
            )
            return redirect('/profile/')
    else:
        form = EmergencyContactForm({
            'emergency_contact_name': civicrm.profile_get_emergency_contact_name(request.user.civicrm_identifier),
            'emergency_contact_phone': civicrm.profile_get_emergency_contact_phone(request.user.civicrm_identifier),
        })

    return render(request, 'member_profile/basic_info_form.html', context={
        'form': form
    })
