#!/usr/bin/env python

import boto3, csv
from dateutil.parser import parse

def cognito_users():
    paginator = boto3.client('cognito-idp').get_paginator('list_users')
    for page in paginator.paginate(UserPoolId='us-east-1_hF6bN5jIG'):
        for user in page['Users']:
            if user['UserStatus'] == 'FORCE_CHANGE_PASSWORD': yield user

with open('users.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Username', 'UserStatus', 'UserCreateDate', 'UserLastModifiedDate'], extrasaction='ignore')
    writer.writeheader()
    for user in cognito_users():
        writer.writerow(user)
