from .models import User

def create_cognito_accounts():
    for user in User.objects.exclude(email=''):
        if user.email == 'ginamlarson@gmail.com':
            continue
        if user.sub != None:
            print('skipping user: ' + user.email)
            continue
        try:
            user.create_cognito_record(True)
        except Exception:
            return user
