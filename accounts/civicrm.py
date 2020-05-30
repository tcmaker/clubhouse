#!/usr/bin/env python

from django.conf import settings
# from accounts.models import User
class User:
    pass

import os, re
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
    return r.json()

def current_member_ids():
    offset = 0
    response = civicrm_query(entity='Membership', method='GET', action='get', options={'offset': offset, 'active_only': 1})
    count = int(response['count'])
    while count > 0:
        for index, membership in response['values'].items():
            print(membership)
            yield membership['contact_id']
        offset += count
        response = civicrm_query(entity='Membership', method='GET', action='get', options={'offset': offset, 'active_only': 1})
        count = int(response['count'])

def import_active_members():
    for contact_id in current_member_ids():
        if contact_id in ['1485']:
            continue
        if User.objects.filter(pk=int(contact_id)).exists():
            continue
        if User.objects.filter(civicrm_identifier=int(contact_id)).exists():
            continue
        print("Importing member: " + contact_id)
        try:
            info = get_member_info(contact_id)
        except IndexError as e:
            print('Could not import ' + contact_id)
            continue

        if info == None:
            print('could not import ' + contact_id)
            continue

        # attempt to build username
        u = User(
            first_name=info['first_name'],
            last_name=info['last_name'],
            email=info['email'],
            username=_make_username(info['first_name'], info['last_name']),
            civicrm_identifier=str(contact_id),
            civicrm_membership_status = 'Current',
        )
        if info['keyfob']:
            u.civicrm_keyfob_code = info['keyfob']
        try:
            u.save()
        except:
            return u

def get_member_info(identifier):
    contact = civicrm_get(entity='Contact', entity_id=identifier)
    if contact == None:
        return None
    keyfob = civicrm_query(entity='Keyfob', method='GET', action='get', options={'contact_id':identifier})

    if keyfob['count'] == 0:
        contact['keyfob'] = None
    else:
        keyfob = keyfob['values'][list(keyfob['values'].keys())[0]]['code']
        contact['keyfob'] = keyfob

    return contact

def civicrm_get(*, entity, entity_id, options={}):
    r = civicrm_query(entity=entity, method='GET', action='get', options={'id': entity_id})
    if len(r['values']) == 0:
        return None
    return r['values'][str(entity_id)]

def create_checksum(user):
    r = civicrm_query(entity='Checksum', method='POST', action='create', options={'contact_id':user.civicrm_identifier})
    return r['values']['checksum']

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

def import_member_by_contact_id(contact_id):
    if User.objects.filter(civicrm_identifier=int(contact_id)).exists():
        raise ValueError('Member already exists in our database')

    # Continue with import
    info = get_member_info(contact_id)

    u = User(
        first_name=info['first_name'],
        last_name=info['last_name'],
        email=info['email'],
        username=_make_username(info['first_name'], info['last_name']),
        civicrm_identifier=str(contact_id),
        # civicrm_membership_status = 'Current',
    )
    if info['keyfob']:
        u.civicrm_keyfob_code = info['keyfob']

    u.save()
    return u

def get_membership_status(contact_id):
    resp = civicrm_query(
        entity='Membership',
        method='GET',
        action='get',
        options={
            'contact_id': contact_id,
            'sort': 'id DESC',
            'rowCount': 1,
        }
    )
    if resp['count'] == 0:
        return None

    key = next(iter(resp['values']))

    status_id = int(resp['values'][key]['status_id'])
    if status_id == 1: return 'New'
    if status_id == 2: return 'Current'
    if status_id == 3: return 'Grace'
    if status_id == 4: return 'Expired'
    if status_id == 5: return 'Pending'

    # It's none of the ones we care about
    return None
