from django.shortcuts import render, redirect
from django.contrib.auth import logout, user_passes_test
from django.contrib import messages

from django.shortcuts import resolve_url

def membership_required(function):
    actual_decorator = user_passes_test(
        lambda u: u.is_current_member,
        login_url = ''
    )
