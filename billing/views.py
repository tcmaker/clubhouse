from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from accounts.auth.decorators import membership_required

from .forms import StripeForm, SubscriptionForm, InvoiceOrAutopayForm, EnrollForm, AutoPayEnrollForm

from functools import wraps
import uuid

import stripe

from .util import api_get, api_patch, uuid_from_url, format_string_from_url

from datetime import datetime

def uses_stripe(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not request.user.stripe_customer_identifier:
            customer = stripe.Customer.create(name=str(request.user))
            request.user.stripe_customer_identifier = customer.id
            request.user.save()

        if 'stripe_idempotency_key' not in request.session:
            request.session['stripe_idempotency_key'] = str(uuid.uuid4())

        return view_func(request, *args, **kwargs)
    return wrapped_view

def uses_person_record(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        person = api_get(request.user.membership_person_record)
        return view_func(request, person, *args, **kwargs)
    return wrapped_view

def uses_household_record(view_func):
    @wraps(view_func)
    def wrapped_view(request, person, *args, **kwargs):
        household = api_get(person['household'])
        return view_func(request, person, household, *args, **kwargs)
    return wrapped_view

# Convenience function
def _enrich_household(household: dict) -> dict:
    household['uuid'] = uuid_from_url(household['url'])
    dt = household['valid_through']

    if dt is not None:
        # Hack, because I can't get strptime to handle the UTC offset correctly
        # See: https://bugs.python.org/issue15873, https://bugs.python.org/msg169952
        if ":" == dt[-3:-2]:
            dt = dt[:-3]+dt[-2:]
        dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S%z')
    household['valid_through'] = dt

    # Fetch the person record for the contact (admin) of the household
    household['contact'] = api_get(household['contact'])


    if household['external_subscription_identifier']:
        # Subscription info from Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        s = {}
        s['subscription'] = stripe.Subscription.retrieve(household['external_subscription_identifier'])
        s['price'] = s['subscription']['items']['data'][0]['price']
        household['stripe_subscription'] = s
    return household

#### Manage Households ####

def household_list(request):
    person = api_get(request.user.membership_person_record)

    return render(request, 'billing/households/index.html', {
        'households': person['administered_households'],
    })


@login_required
@uses_stripe
@uses_person_record
@uses_household_record
def household_detail(request, person, household, uuid):
    url_pattern = format_string_from_url(person['household'])
    url = url_pattern % uuid
    detail_household = api_get(url)

    # permission check
    if detail_household['contact'] != person['url']:
        message.error('You are not the contact for this household')
        return redirect('/billing/')

    _enrich_household(detail_household)

    subscription = stripe.Subscription.retrieve(detail_household['external_subscription_identifier'])

    return render(request, 'billing/households/detail.html', {
        'household': detail_household,
        'subscription_info': subscription,
    })

@login_required
@uses_stripe
@uses_person_record
@uses_household_record
def household_form(request, person, household, uuid):
    url_pattern = format_string_from_url(person['household'])
    url = url_pattern % uuid
    detail_household = api_get(url)

    # permission check
    if detail_household['contact'] != person['url']:
        message.error('You are not the contact for this household')
        return redirect('/billing/')

    if request.method == 'POST':
        pass

    return

@login_required
def index(request):
    person = api_get(request.user.membership_person_record)

    # For display purposes, we want to modify the data coming back from the
    # billing system
    temp_list = []
    for household in person['administered_households']:
        if household['url'] != person['household']:
            _enrich_household(household)
            temp_list.append(household)
    person['administered_households'] = temp_list

    household = None
    student_team = None

    if person['household']:
        household = _enrich_household(api_get(person['household']))

    if person['student_team']:
        student_team = _enrich_household(api_get(person['student_team']))

    return render(request, 'billing/index.html', {
        'person': person,
        'household': household,
        'student_team': student_team,
    })

@login_required
@membership_required
@uses_stripe
def card_form(request):
    #TODO: Move as much Stripe stuff as possible into the billing system
    if request.method == 'POST':
        form = StripeForm(request.POST)

        if form.is_valid():
            payment_method_id = form.cleaned_data['stripe_token']
            print(payment_method_id)
            resp = stripe.SetupIntent.confirm(request.session['setup_intent_id'], payment_method=payment_method_id)
            if resp.status == 'succeeded':
                # Use the new card for future billing
                stripe.Customer.modify(
                    request.user.stripe_customer_identifier,
                    invoice_settings = {
                        'default_payment_method': payment_method_id,
                    }
                )
                # Get customer's existing payment methods and detatch them.
                payment_methods = stripe.PaymentMethod.list(customer=request.user.stripe_customer_identifier, type="card").data
                for pm in payment_methods:
                    if pm.id == payment_method_id:
                        continue
                    else:
                        print(pm.id)
                        stripe.PaymentMethod.detach(pm.id)

                # Remove the SetupIntent from the session, as we no longer need it
                del request.session['setup_intent_id']

                messages.success(request, "Card information updated.")
                return redirect('/billing/')

    else:
        # setup intent
        intent = stripe.SetupIntent.create(
            customer = request.user.stripe_customer_identifier,
            usage = "off_session",
        )
        request.session['setup_intent_id'] = intent.id

        form = StripeForm()

    return render(request, 'billing/card_form.html', {
        'form': form,
    })

def subscription_detail(request):
    return render(request, 'billing/subscription_detail.html', {})

@login_required
@membership_required
@uses_stripe
def subscription_form(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
    else:
        form = SubscriptionForm(initial={
            'plan': SubscriptionForm.SIX_MONTH_PLAN,
        })
    return render(request, 'billing/subscription_form.html', {
        'form': form
    })

@login_required
@uses_stripe
@uses_person_record
@uses_household_record
def enroll_autopay_form(request, person, household):
    api_patch(household['url'], {
        'external_customer_identifier': request.user.stripe_customer_identifier,
    })

    if request.method == 'POST':
        form = AutoPayEnrollForm(request.POST)
        if form.is_valid():
            if form.is_valid():
                payment_method_id = form.cleaned_data['stripe_token']
                print(payment_method_id)
                resp = stripe.SetupIntent.confirm(request.session['setup_intent_id'], payment_method=payment_method_id)
                if resp.status == 'succeeded':
                    # Use the new card for future billing
                    stripe.Customer.modify(
                        request.user.stripe_customer_identifier,
                        invoice_settings = {
                            'default_payment_method': payment_method_id,
                        }
                    )
                    # Get customer's existing payment methods and detatch them.
                    payment_methods = stripe.PaymentMethod.list(customer=request.user.stripe_customer_identifier, type="card").data
                    for pm in payment_methods:
                        if pm.id == payment_method_id:
                            continue
                        else:
                            print(pm.id)
                            stripe.PaymentMethod.detach(pm.id)

                    # Remove the SetupIntent from the session, as we no longer need it
                    del request.session['setup_intent_id']

                    subscription = _stripe_create_autopay_subscription(request, form)
                    api_patch(household['url'], {
                        'external_customer_identifier': request.user.stripe_customer_identifier,
                        'auto_renew': True,
                        'external_subscription_identifier': subscription.id,
                    })
                    messages.success(request, 'Your subscription has been created.')

                    if 'stripe_idempotency_key' in request.session:
                        del request.session['stripe_idempotency_key']

                    request.session['temporarily_allow_access'] = True
                    return redirect('/')

    else:
        # setup intent
        intent = stripe.SetupIntent.create(
            customer = request.user.stripe_customer_identifier,
            usage = "off_session",
        )
        request.session['setup_intent_id'] = intent.id

        form = AutoPayEnrollForm(initial={
            'plan': AutoPayEnrollForm.ONE_MONTH_PLAN,
        })

    return render(request, 'billing/enroll_autopay_form.html', {
        'form': form
    })

@login_required
@uses_stripe
@uses_person_record
@uses_household_record
def enroll_invoice_form(request, person, household):
    if request.method == 'POST':
        form = EnrollForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['plan'])
            subscription = _stripe_create_invoiced_subscription(request, form)
            api_patch(household['url'], {
                'external_customer_identifier': request.user.stripe_customer_identifier,
                'external_subscription_identifier': subscription.id,
            })
            messages.success(request, 'Your subscription has been created. Check your email for your invoice.')
            request.session['temporarily_allow_access'] = True

            if 'stripe_idempotency_key' in request.session:
                del request.session['stripe_idempotency_key']

            return redirect('/')
    else:
        form = EnrollForm(initial={
            'plan': AutoPayEnrollForm.ONE_MONTH_PLAN,
        })

    return render(request, 'billing/enroll_form.html', {
        'form': form
    })

def _stripe_create_autopay_subscription(request, form):
    stripe_prices = {
        form.ONE_MONTH_PLAN: settings.STRIPE_PRODUCT_ONE_MONTH_PLAN,
        form.SIX_MONTH_PLAN: settings.STRIPE_PRODUCT_SIX_MONTH_PLAN,
        form.TWELVE_MONTH_PLAN: settings.STRIPE_PRODUCT_TWELVE_MONTH_PLAN,
    }

    price = stripe_prices[form.cleaned_data['plan']]

    subscription = stripe.Subscription.create(
        customer=request.user.stripe_customer_identifier,
        items=[
            {'price': price}
        ],
        collection_method='charge_automatically',
        # payment_behavior='default_incomplete',
        idempotency_key=request.session['stripe_idempotency_key'],
        proration_behavior='none',
        off_session=False,
    )

    return subscription

def _stripe_create_invoiced_subscription(request, form):
    stripe_prices = {
        form.ONE_MONTH_PLAN: settings.STRIPE_PRODUCT_ONE_MONTH_PLAN,
        form.SIX_MONTH_PLAN: settings.STRIPE_PRODUCT_SIX_MONTH_PLAN,
        form.TWELVE_MONTH_PLAN: settings.STRIPE_PRODUCT_TWELVE_MONTH_PLAN,
    }

    price = stripe_prices[form.cleaned_data['plan']]

    subscription = stripe.Subscription.create(
        customer=request.user.stripe_customer_identifier,
        items=[
            {'price': price}
        ],
        collection_method='send_invoice',
        days_until_due=7,
        payment_behavior='default_incomplete',
        idempotency_key=request.session['stripe_idempotency_key'],
        proration_behavior='none'
    )
    del request.session['stripe_idempotency_key']
    return subscription
