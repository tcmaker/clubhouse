from django.shortcuts import render, redirect
from accounts.auth.decorators import membership_required
from django.contrib.auth.decorators import login_required

@login_required
@membership_required
def index(request):
    # if not request.user.is_authenticated:
    #     return redirect('/oidc/authenticate')
    return render(request, 'dashboard/index.html', {
    })
