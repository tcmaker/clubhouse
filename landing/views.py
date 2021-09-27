from django.shortcuts import render, redirect

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'landing/index.html', {})

    # Used when a subscription was just created seconds ago, but we haven't
    # received round-trip notification yet
    if 'temporarily_allow_access' in request.session:
        return render(request, 'dashboard/index.html', {})

    if not request.user.is_enrolled:
        return redirect('/billing/enroll/')

    if not request.user.is_current_member:
        return redirect('/billing/')

    # We're all good
    return render(request, 'dashboard/index.html', {})
