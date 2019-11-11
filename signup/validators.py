from django.core.exceptions import ValidationError
import re

def validate_auth0_password(password):
    # Must contain 8 or more characters
    if not re.match('(?=.{8,})', password):
        raise ValidationError('Password must contain 8 or more characters')

    if not re.match('(?=.*\d)', password):
        raise ValidationError('Password must contain a digit')

    if not re.match('(?=.*[a-z])', password):
        raise ValidationError('Password must contain a lower case character')

    if not re.match('(?=.*[A-Z])', password):
        raise ValidationError('Password must contain an upper case character')

    if not re.match('(?=.*[\!@#%\^\&\*\$])', password):
        raise ValidationError('Password must contain a symbol')
