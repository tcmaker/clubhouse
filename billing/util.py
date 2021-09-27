from django.conf import settings
import requests

from datetime import datetime, timedelta

from urllib.parse import urlparse

REQUEST_HEADERS = {
    'Authorization': 'Bearer %s' % settings.BILLING_SYSTEM_API_TOKEN
}

def api_get(url):
    resp = requests.get(url, headers=REQUEST_HEADERS)
    return resp.json()

def api_post(url, json):
    resp = requests.post(url, json=json, headers=REQUEST_HEADERS)
    return resp.json()

def api_patch(url, json):
    resp = requests.patch(url, json=json, headers=REQUEST_HEADERS)
    return resp.json()


#### TODO: Modify API to include bare UUID inside JSON object ####

def uuid_from_url(url: str) -> str:
    path = urlparse(url).path
    path = path.strip('/') # leading and trailing slashes screw up split()
    path = path.split('/')
    return path[-1] # UUID is always last item in path

def format_string_from_url(url: str) -> str:
    parts = urlparse(url)
    path = parts.path
    path = path.strip('/')
    path = path.split('/')
    path[-1] = '%s'
    path = '/'.join(path)
    rebuilt_url = "{scheme}://{netloc}/{path}/".format(
        scheme=parts.scheme,
        netloc=parts.netloc,
        path=path
    )
    return rebuilt_url

def compute_subscription_start_date(end_date: datetime) -> datetime:
    return end_date - timedelta(days=30)
