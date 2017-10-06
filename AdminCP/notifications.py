from models import Notification
from PiLock.settings import DEBUG
from django.db import IntegrityError

def check_for_debug_mode():
    if DEBUG:
        try:
            Notification.objects.create(type="DEBUG")
        except IntegrityError:
            pass
    else:
        Notification.objects.filter(type="DEBUG").delete()