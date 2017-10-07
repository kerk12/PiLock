# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.

class Notification(models.Model):
    TYPES = (
        ("DEBUG", "Debug Mode"),
        ("UPDATE", "Update available"),
        ("SEC", "Security Issue"),
    )

    # Only one notification created for each type.
    type = models.CharField(max_length=10, choices=TYPES, default="DEBUG", unique=True)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
