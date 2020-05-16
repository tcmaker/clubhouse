from django.shortcuts import render

from .civicrm import renewal_url

def index(request):
    return render(request, 'renew/index.html', {
        'renewal_url': renewal_url(request.user),
    })
