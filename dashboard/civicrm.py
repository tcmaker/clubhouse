#!/usr/bin/env python

from django.conf import settings
from localflavor.us.us_states import US_STATES
import os
import requests

url_base = settings.CIVICRM_URL_BASE

def civicrm_query(*, entity, method, action, options):
    params = {
        'key': settings.CIVICRM_SITE_KEY,
        'api_key': settings.CIVICRM_API_KEY,
        'entity': entity,
        'action': action,
        'json': '1',
    }
    params = {**params, **options}

    if method == 'POST':
        func = requests.post
    else:
        func = requests.get

    r = func(settings.CIVICRM_API_URL_BASE, params)
    r.raise_for_status()
    return r

def civicrm_get(*, entity, id, options):
    r = civicrm_query(entity=entity, method='GET', action='get', options={'id': id})
    return r.json()['values'][str(id)]

def create_checksum(user):
    r = civicrm_query(entity='Checksum', method='POST', action='create', options={'contact_id':user.civicrm_identifier})
    r.raise_for_status()
    return r.json()['values']['checksum']

def expand_url(uri):
    return settings.CIVICRM_URL_BASE + uri

def renewal_url(user):
    return expand_url('&'.join([
        'civicrm/contribute/transact',
        'reset=1',
        'id=4',
        'cs=%s' % create_checksum(user),
        'cid=%s' % user.civicrm_identifier
    ]))

def _extract_value_after_create(response):
    '''
        CiviCRM's API makes a lot of PHP-specific assumptions that make
        it hard to process responses in other programming languages. This
        method extracts a created value from an API response.
    '''

    response.raise_for_status() # Raise exception on failure
    # import code; code.interact(local=dict(globals(), **locals()))
    entity = response.json()['values'] # parse JSON and extract values dictionary
    entity = entity.values() # Just get the dict values, disregard the keys
    entity = iter(entity) # Convert into an iterable object
    entity = next(entity) # Grab the first (and only) item
    return entity # Return that value

def signup_create_contact(properties):
    default_options = {
        'contact_type': 'Individual',
    }

    properties = {**default_options, **properties}

    if settings.CIVICRM_FIELD_ACCEPTED_LIABILITY_WAIVER not in properties:
        properties[settings.CIVICRM_FIELD_ACCEPTED_LIABILITY_WAIVER] = 1

    r = civicrm_query(
        entity='Contact',
        method='POST',
        action='create',
        options=properties
    )
    return _extract_value_after_create(r)

def _expand_state_id(s):
    if s == 'MN': return 'Minnesota'
    # expand state abbreviations, if necessary
    for abbreviation, full_name in list(US_STATES):
        print("%s: %s" % (abbreviation, full_name))
        if s == abbreviation: return str(full_name)

def signup_add_address(contact_id, properties):
    '''
        properties should look like:

        {
            'street_address': "123 Sesame Street",
            'supplemental_address_1': "optional second line for street address",
            'city': 'Minneapolis',
            'state_province_id': 'Minnesota',
            'postal_code': '55406',
        }
    '''

    print(properties)

    default_options = {
        'contact_id': contact_id,
        'location_type': 'Main',
        'is_primary': 1,
    }

    properties = {**default_options, **properties}

    if 'state_province_id' not in properties:
        properties['state_province_id'] = 'MN'

    properties['state_province_id'] = _expand_state_id(properties['state_province_id'])

    r = civicrm_query(
        entity='Address',
        method='POST',
        action='create',
        options=properties
    )
    return _extract_value_after_create(r)

def signup_add_email(contact_id, email):
    properties = {
        'contact_id': contact_id,
        'email': email,
        'is_primary': 1,
        'location_type_id': 'Main',
    }

    return _extract_value_after_create(civicrm_query(
        entity = 'Email',
        method = 'POST',
        action = 'create',
        options = properties
    ))

def signup_add_phone(contact_id, phone, can_receive_sms):
    if can_receive_sms:
        phone_type = 'Mobile'
    else:
        phone_type = 'Phone'

    properties = {
        'contact_id': contact_id,
        'is_primary': 1,
        'location_type_id': 'Main',
        'phone_type_id': phone_type,
        'phone': str(phone),
    }

    return _extract_value_after_create(civicrm_query(
        entity = 'Phone',
        method = 'POST',
        action = 'create',
        options = properties
    ))

def signup_add_emergency_contact(contact_id, emergency_contact_name, emergency_contact_phone):
    contact = civicrm_get(entity='Contact', id=contact_id, options={})
    contact[settings.CIVICRM_FIELD_EMERGENCY_CONTACT_NAME] = emergency_contact_name
    contact[settings.CIVICRM_FIELD_EMERGENCY_CONTACT_PHONE] = emergency_contact_phone
    return signup_create_contact(contact)

def signup_accept_liability_waiver(contact_id):
    contact = civicrm_get(entity='Contact', id=contact_id, options={})
    contact[settings.CIVICRM_FIELD_ACCEPTED_LIABILITY_WAIVER] = 1
    print(settings.CIVICRM_FIELD_ACCEPTED_LIABILITY_WAIVER)

    return signup_create_contact(contact)

def signup_add_keyfob_code(contact_id, keyfob_code):
    properties = {
        'contact_id': contact_id,
        'code': keyfob_code,
        'access_level': 1,
    }

    return _extract_value_after_create(civicrm_query(
        entity = 'Keyfob',
        method = 'POST',
        action = 'create',
        options = properties
    ))

def signup_add_current_membership(contact_id):
    properties = {
        'contact_id': contact_id,
        'membership_type_id': 'Monthly Membership',
        'status_id': 'Current'
    }

    return _extract_value_after_create(civicrm_query(
        entity = 'Membership',
        method = 'POST',
        action = 'create',
        options = properties
    ))
