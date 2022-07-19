from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def membership_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # This is used when a subscription was created or updated seconds ago,
        # but we haven't had time for the round-trip notificatio
        if 'temporarily_allow_access' in request.session and request.session['temporarily_allow_access']:
            return view_func(request, *args, **kwargs)

        # Allow inactive users to access the billing section
        if request.user.is_inactive_member and request.path.startswith('/billing/'):
            return view_func(request, *args, **kwargs)

        if not request.user.is_current_member and 'temporarily_allow_access' not in request.session:
            messages.error(request, 'You must be a current member to access this resource.')
            return redirect('/billing/')

        return view_func(request, *args, **kwargs)
    return wrapped_view
