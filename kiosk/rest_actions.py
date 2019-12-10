import requests
import os

def http_client():
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + os.environ['MEMBERSHIP_API_TOKEN']})
    return session

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
