from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.contrib.auth import logout
from . import rest_actions
from .forms import DuesForm

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from . import rest_actions
from django.utils.dateparse import parse_datetime
from mozilla_django_oidc.views import OIDCLogoutView as MozillaLogoutView

import stripe, os, datetime

from django.conf import settings

class OIDCLogoutView(MozillaLogoutView):
    def get(self, request):
        # import code; code.interact(local=dict(globals(), **locals()))
        return self.post(request)

def login(request):
#    import code; code.interact(local=dict(globals(), **locals()))
    if request.user.is_authenticated:
        return redirect('/dashboard')

    # Initialze the OIDC view
    return redirect('/oidc/authenticate')



@login_required
def index(request):
    # if not request.user.is_authenticated:
    #     return redirect('/oidc/authenticate')
    return render(request, 'dashboard/index.html', {
    })

@login_required
def index_old(request):
    # Redirect to payment page unless membership is active

    # # TODO: move this check into a decorator
    # if not request.user.has_active_membership():
    #     return redirect('/dashboard/activate')

    # Membership Info
    household = None
    student_team = None
    member = rest_actions.get_member_by_uuid(request.user.member_identifier)
    if member['household']:
        household = rest_actions.get_resource(member['household'])
        household['valid_through'] = parse_datetime(household['valid_through'])
        household['dues_plan'] = rest_actions.get_dues_plan(household['dues_plan'])
    elif member['student_team']:
        student_team = rest_actions.get_resource(member['student_team'])
        student_team['valid_through'] = parse_datetime(student_team['valid_through'])

    # Storage
    green_tags = request.user.green_tags_issued.all()
    red_tags = request.user.red_tag_violations.all()
    try:
        cubby = request.user.cubby
    except:
        cubby = None

    # Endorsements
    endorsements = []

    context = {
        'member': member,
        'household': household,
        'student_team': student_team,
        'green_tags': green_tags,
        'red_tags': red_tags,
        'cubby': cubby
    }

    return render(request, 'dashboard/index.html', context)

class ActivateMembershipForm(LoginRequiredMixin, FormView):
    template_name = 'dashboard/activate.html'
    form_class = DuesForm

    def form_valid(self, form):
        stripe.api_key = os.environ['STRIPE_SECRET_KEY']
        household = self.request.user.get_household()
        if household['external_customer_identifier']:
            stripe_customer = stripe.Customer.retrieve(household['external_customer_identifier'])
        else:
            stripe_customer = stripe.Customer.create(
                name = ', '.join([
                    self.request.user.last_name,
                    self.request.user.first_name,
                ]),
                email = self.request.user.email,
            )
        stripe_customer.source = form.cleaned_data['stripe_token']
        stripe_customer.save()
        dues_plan = rest_actions.get_dues_plan(form.cleaned_data['dues_plan'])
        if dues_plan['requires_setup_fee']:
            stripe.InvoiceItem.create(
                customer=stripe_customer,
                amount=2000, # $20.00 is 2000 pennies
                currency="usd",
                description="One-time setup fee"
            )

        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer,
            items=[
                { "plan": dues_plan['stripe_plan_identifier'] },
            ]
        )
        resp = rest_actions.update_household(household['url'], {
            'external_customer_identifier': stripe_customer.id,
            'external_subscription_identifier': stripe_subscription.id,
            'valid_through': str(datetime.datetime.fromtimestamp(stripe_subscription.current_period_end)),
            'dues_plan': dues_plan['url'],
            'status': 'active',
        })
        import code; code.interact(local=dict(globals(), **locals()))
        return redirect('/dashboard/')
