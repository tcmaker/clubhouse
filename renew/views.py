from django.shortcuts import render
from accounts.auth.decorators import membership_required
from django.contrib.auth.decorators import login_required

from .civicrm import renewal_url

@login_required
@membership_required
def index(request):
    return render(request, 'renew/index.html', {
        'renewal_url': renewal_url(request.user),
    })
