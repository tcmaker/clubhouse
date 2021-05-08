from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Product
from .forms import HourlyForm

import stripe
import json

@login_required
def product_list(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    products = Product.objects.all()

    return render(request, 'consumables/product_list.html', {
        'products': products
    })

@login_required
def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)

    # To Do: get other consumable types
    form_class = HourlyForm

    form = form_class(initial={'product_id': product.id})

    return render(request, 'consumables/product_detail.html', {
        'product': product,
        'form': form,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

@login_required
def generate_stripe_session(request, product_id):
    product = Product.objects.get(pk=product_id)
    request_payload = request.POST
    print(request_payload)

    quantity = int(request_payload['quantity'][0])

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Create stripe customer, if necessary
    if not request.user.stripe_customer_identifier:
        customer = stripe.Customer.create(name=str(request.user))
        request.user.stripe_customer_identifier = customer.id
        request.user.save()

    # Get the price of the product
    stripe_price = stripe.Price.list(product=product.stripe_product_identifier).data[0]

    stripe_session = stripe.checkout.Session.create(
        success_url=settings.WEBAPP_URL_BASE + '/consumables/callback/?status=success',
        cancel_url=settings.WEBAPP_URL_BASE + '/consumables/callback/?status=canceled',
        customer=request.user.stripe_customer_identifier,
        line_items=[
            {
                'price': stripe_price.id,
                'quantity': quantity,
            }
        ],
        payment_method_types=['card'],
        mode='payment',
    )

    return JsonResponse(stripe_session)

def callback(request):
    status = request.GET.get('status')
    if status == 'success':
        messages.add_message(request, messages.SUCCESS, 'Your payment is complete')
    if status == 'canceled':
        messages.add_message(request, messages.INFO, 'Your payment was canceled')
    return redirect('/consumables/')
