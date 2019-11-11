from django.shortcuts import render
from django.views import View

from django.contrib.auth.decorators import login_required, permission_required

@login_required
def index(request):
    # Membership Info
    member = request.user.member
    membership = member.membership

    # Storage
    green_tags = member.green_tags_issued.all()
    red_tags = member.red_tag_violations.all()
    try:
        cubby = member.cubby
    except:
        cubby = None

    # Endorsements
    endorsements = []

    context = {
        'member': member,
        'membership': membership,
        'green_tags': green_tags,
        'red_tags': red_tags,
        'cubby': cubby
    }

    return render(request, 'dashboard/index.html', context)
