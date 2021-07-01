from django.shortcuts import render, redirect
from accounts.auth.decorators import membership_required
from django.contrib.auth.decorators import login_required

# @login_required
# @membership_required
# def index(request):
#     return render(request, 'dashboard/index.html', {
#     })

def index(request):
    return redirect('/')
