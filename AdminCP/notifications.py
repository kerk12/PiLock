from .models import Notification
from PiLock.settings import DEBUG
from django.db import IntegrityError
from .update_checker import UpdateChecker, UpdateCheckError


def check_for_debug_mode():
    if DEBUG:
        create_notification("DEBUG")
    else:
        delete_notification("DEBUG")

def check_for_updates_and_notify():
    uc = UpdateChecker()
    try:
        create_notification("UPDATE") if uc.check_for_updates() else delete_notification("UPDATE")
    except UpdateCheckError:
        create_notification("UPDATE", "Could not check for updates.")


# TODO: Unify the next two functions...

def create_notification(type, text=""):
    delete_notification(type)
    try:
        Notification.objects.create(type=type, text=text)
    except IntegrityError:
        pass

def delete_notification(type):
    Notification.objects.filter(type=type).delete()