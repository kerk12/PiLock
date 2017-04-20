from __future__ import unicode_literals

from django.db import models
from django.conf import settings


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    authToken = models.CharField(max_length=64, blank=True, null=False)
    pin = models.CharField(max_length=6, default="123456")
