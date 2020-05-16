#!/usr/bin/env python

from django.conf import settings

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
