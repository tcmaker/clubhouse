from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as tz_now
from django.conf import settings
from datetime import timedelta
import json, uuid
import boto3

from accounts.models import User

class Command(BaseCommand):
    help = "Sends test messages to the SQS queue"

    def __make_json_message(self, action):
        u = User.objects.first()
        msg = {
            'member_identifier': u.email,
            'keyfob_code': u.civicrm_keyfob_code,
            'effective_priority': 1,
            'action': action,
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
        message = self.__make_json_message('enable')
        self.__enqueue(message)
        print(message)
        message = self.__make_json_message('disable')
        self.__enqueue(message)
        print(message)
