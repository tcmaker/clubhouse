import requests
import os, sys

def http_client():
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + os.environ['MEMBERSHIP_API_TOKEN']})
    return session

def get_dues_plan(url):
    client = http_client()
    return client.get(url).json()

def create_member(attributes):
    client = http_client()
    return client.post(os.environ['MEMBERSHIP_API_URL_BASE'] + '/persons/', json=attributes).json()

def create_household(attributes):
    client = http_client()
    return client.post(os.environ['MEMBERSHIP_API_URL_BASE'] + '/households/', json=attributes).json()

def update_member(url, attributes):
    return http_client().patch(url, attributes).json()
