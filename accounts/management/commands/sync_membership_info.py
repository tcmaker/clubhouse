from django.core.management.base import BaseCommand, CommandError
from accounts.models import User
import time

class Command(BaseCommand):
    help = "Syncs membership info from CiviCRM"

    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.civicrm_identifier:
                print(user)
                user.sync_membership_info()
                time.sleep(1)
