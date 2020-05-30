from .models import Cubby

def prepopulate():
    for i in range(1, 177):
        Cubby.objects.create(identifier=str(i))
