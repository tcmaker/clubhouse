from django.utils.timezone import now as tz_now
from django.utils.timezone import make_aware
from django.db.transaction import atomic
# from membership.models import Member, Membership, PaymentPlan
import os, stripe, datetime
from . import rest_actions
from dashboard.models import User

def approve_signup(signup, keyfob_code):
    signup.data['person']['member_since'] = str(tz_now().date())
    signup.data['person']['keyfob_code'] = keyfob_code
    dues_plan = rest_actions.get_dues_plan(signup.data['dues']['dues_plan'])

    member = rest_actions.create_member(signup.data['person'])

    # Look up user by Username
    user = User.objects.filter(username=signup.data['person']['username']).first()
    uuid = member['url'].rstrip('/').split('/')[-1]
    user.member_identifier = uuid
    user.save()

    import code; code.interact(local=dict(globals(), **locals()))

    json = {
        'name': member['family_name'] + " Household",
        'valid_through': str(tz_now()), # Stripe will tell us the real date,
        'status': 'incomplete',
        'auto_renew': False,
        'contact': member['url'],
        'dues_plan': dues_plan['url']
    }
    household = rest_actions.create_household(json)
    import code; code.interact(local=dict(globals(), **locals()))

    resp = rest_actions.update_member(member['url'], {
        'household': household['url'],
    })

    signup.membership_activation_completed_at = tz_now()
    signup.save()

    return (member, household)
