#!/usr/bin/env python

import boto3

client = boto3.client('cognito-idp')

function create_user
response = client.admin_create_user(
    UserPoolId='us-east-1_hF6bN5jIG',
    Username='stephen',
    UserAttributes=[
        {'Name': 'email', 'Value': 'stephen@vandahm.com'},
        {'Name': 'family_name', 'Value': 'Van Dahm'},
        {'Name': 'given_name', 'Value': 'Stephen'},
        {'Name': 'preferred_username', 'Value': 'stephen'},
    ],
    DesiredDeliveryMediums=['EMAIL']
)


