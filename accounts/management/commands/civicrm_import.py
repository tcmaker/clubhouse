from django.core.management.base import BaseCommand, CommandError
from accounts.models import User
import csv
import boto3

class Command(BaseCommand):
    help = "Performs a mass import of members from a CiviCRM dump"

    def handle(self, *args, **options):
        pass
