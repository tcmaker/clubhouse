from django.utils.timezone import now as tz_now
from django.utils.timezone import make_aware
from django.db.transaction import atomic
#from membership.models import Member, Membership, PaymentPlan
from .models import Invitation
import os, stripe, datetime

@atomic
def approve_household(household):
    # Member record
    member = Member()
    for key, value in household.data.items():
        setattr(member, key, value)
    member.member_since = tz_now()
    member.save()

    # Membership record
    membership = Membership()
    membership.membership_contact = member
    membership.membership_type = 'household'
    membership.payment_method = household.data['payment_method']
    membership.payment_plan = PaymentPlan.objects.get(pk=int(household.data['payment_plan_id']))
    membership.valid_through = tz_now() # Stripe will tell us the real end date.
    membership.stripe_customer_identifier = household.data['stripe_customer_identifier']
    membership.save()

    # Associate member with membership record
    member.membership = membership
    member.save()

    # Activate Stripe Subscription
    stripe.api_key = os.environ['STRIPE_SECRET_KEY']
    if membership.payment_plan.requires_setup_fee:
        stripe.InvoiceItem.create(
            customer=membership.stripe_customer_identifier,
            amount=2000, # $20.00 is 2000 pennies
            currency="usd",
            description="One-time setup fee"
        )

    subscription = stripe.Subscription.create(
        customer=membership.stripe_customer_identifier,
        items=[
            { "plan": membership.payment_plan.stripe_plan_identifier },
        ]
    )
    membership.stripe_subscription_identifier = subscription.id
    membership.valid_through = make_aware(datetime.datetime.fromtimestamp(subscription.current_period_end))
    membership.save()

    # Associate invitations with the membership
    invitations = Invitation.objects.filter(signup_progress_id=household.id).all()
    for i in invitations:
        i.membership = membership
        i.save()

    # Update original signup record
    household.membership_activation_completed_at = tz_now()
    household.save()

    return (member, membership, household)

@atomic
def approve_invitation(invitation):
    # Member record
    member = Member()
    for key, value in invitation.data.items():
        setattr(member, key, value)
    member.member_since = tz_now()
    member.membership = Membership.objects.get(pk=invitation.membership_id)
    member.save()

    invitation.member = member
    invitation.membership = member.membership
    invitation.membership_activation_completed_at = tz_now()
    invitation.save()
