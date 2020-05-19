from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as tz_now
from django.conf import settings
from datetime import timedelta
import json, uuid
import boto3

from timeslots.models import Timeslot

class Command(BaseCommand):
    help = "Enables member keyfobs for the next timeslot"

    def __make_json_message(self, keyfob_code, member_identifier='None'):
        msg = {
            'member_identifier': member_identifier,
            'keyfob_code': keyfob_code,
            'effective_priority': 1,
            'action': 'enable',
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
        begin_range = tz_now()
        end_range = begin_range + timedelta(minutes=10)
        timeslots = Timeslot.objects.filter(start_time__gte=begin_range, start_time__lte=end_range)

        for timeslot in timeslots:
            for reservation in timeslot.reservation_set.all():
                message = self.__make_json_message(reservation.member.civicrm_keyfob_code, reservation.member.email)
                self.__enqueue(message)
                print(message)
