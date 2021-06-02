from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Department

import stripe
import json
from decimal import Decimal

@login_required
def index(request):
    return redirect('/workshop/departments/')

@login_required
def department_list(request):
    departments = Department.objects.order_by('name').all()

    return render(request, 'workshop/department_list.html', {
        'departments': departments,
    })

@login_required
def department_detail(request, department_id):
    department = Department.objects.get(slug=department_id)

    return render(request, 'workshop/department_detail.html', {
        'department': department,
    })

@login_required
def department_donate(request, department_id):
    department = Department.objects.get(slug=department_id)

    return render(request, 'workshop/department_donate.html', {
        'department': department,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

@login_required
def department_checkout(request, department_id):
    department = Department.objects.get(slug=department_id)
    request_payload = request.POST
    print(request_payload)

    amount = request_payload['amount']

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Create stripe customer, if necessary
    if not request.user.stripe_customer_identifier:
        customer = stripe.Customer.create(name=str(request.user))
        request.user.stripe_customer_identifier = customer.id
        request.user.save()

    print('amount: ' + amount)
    amount = Decimal(amount)
    amount = int(amount * 100)
    print(amount)

    stripe_session = stripe.checkout.Session.create(
        success_url=settings.WEBAPP_URL_BASE + department.get_absolute_url() + 'donate/callback/?status=success',
        cancel_url=settings.WEBAPP_URL_BASE + department.get_absolute_url() + 'donate/callback/?status=canceled',
        customer=request.user.stripe_customer_identifier,
        line_items=[
            {
                'price_data': {
                    'unit_amount': amount,
                    'currency': 'usd',
                    'product': department.stripe_donation_product_identifier
                },
                'quantity': 1,
            }
        ],
        payment_method_types=['card'],
        mode='payment',
    )

    return JsonResponse(stripe_session)

def department_checkout_callback(request, department_id):
    department = Department.objects.get(slug=department_id)

    # Do we need to process a success or cancel message?
    if request.GET.get('status') == 'success':
        messages.success(request, 'Thank you for your donation!')
    if request.GET.get('status') == 'canceled':
        messages.info(request, 'Donation canceled.')

    return redirect(department.get_absolute_url())
