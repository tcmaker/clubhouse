from django.conf import settings


def extra_settings(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }
