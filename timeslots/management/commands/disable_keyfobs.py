from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as tz_now
from django.conf import settings
from datetime import timedelta
import json, uuid
import boto3

from timeslots.models import Timeslot

class Command(BaseCommand):
    help = "Disables keyfobs for the most recently-ended timeslot"

    def __make_json_message(self, keyfob_code, member_identifier='None'):
        msg = {
            'member_identifier': member_identifier,
            'keyfob_code': keyfob_code,
            'effective_priority': 0,
            'action': 'disable',
        }
        return json.dumps(msg)

    def __enqueue(self, message):
        client = boto3.client('sqs')
        client.send_message(
            QueueUrl=settings.TIMESLOT_QUEUE_URL,
            MessageBody=message,
            MessageDeduplicationId=str(uuid.uuid4()),
            MessageGroupId="TIMESLOT_KEYFOB"
        )

    def handle(self, *args, **options):
        end_range = tz_now()
        begin_range = end_range - timedelta(minutes=30)
        timeslots = Timeslot.objects.filter(end_time__gte=begin_range, end_time__lte=end_range)

        for timeslot in timeslots:
            for reservation in timeslot.reservation_set.all():
                message = self.__make_json_message(reservation.member.civicrm_keyfob_code, reservation.member.email)
                self.__enqueue(message)
                print(message)
