from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def membership_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_current_member:
            messages.error(request, 'You must be a current member to access this resource.')
            return redirect('/renew')
        return view_func(request, *args, **kwargs)
    return wrapped_view
