from __future__ import unicode_literals

from django.db import models
from django.conf import settings


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Hashed fields below. Length set to 130 characters, to accommodate SHA512.
    authToken = models.CharField(max_length=130)
    pin = models.CharField(max_length=130, blank=True)
    wearToken = models.CharField(max_length=130, blank=True)


class AccessAttempt(models.Model):
    usernameEntered = models.CharField(max_length=150, blank=True)
    is_unlock_attempt = models.BooleanField(default=False)
    successful = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(protocol="IPv4", default="0.0.0.0")
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        output = ""
        if self.is_unlock_attempt:
            output += "UNLOCK | "
        else:
            output += "LOGIN | "
        if self.usernameEntered:
            output += self.usernameEntered + " | "

        output += str(self.datetime) + " | "
        output += self.ip + " | "

        if self.successful:
            output += "SUCCESS"
        else:
            output += "FAILURE"

        return unicode(output)

