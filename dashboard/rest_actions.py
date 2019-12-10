import requests
import os,sys

def http_client():
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + os.environ['MEMBERSHIP_API_TOKEN']})
    return session

def get_resource(url):
    client = http_client()
    return client.get(url).json()

def get_member_by_uuid(uuid):
    url = os.environ['MEMBERSHIP_API_URL_BASE'] + '/persons/' + str(uuid)
    return get_resource(url)

def dues_plans():
    client = http_client()
    plans = client.get(os.environ['MEMBERSHIP_API_URL_BASE'] + '/dues_plans/')
    plans = plans.json()
    plans = sorted(plans, key=lambda i: i['sort_priority'])
    plans = [(x['url'], x['name']) for x in plans]
    return plans

def get_dues_plan(url):
    client = http_client()
    return client.get(url).json()

def update_household(url, attributes):
    return http_client().patch(url, json=attributes).json()
