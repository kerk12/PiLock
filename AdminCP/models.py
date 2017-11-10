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

    TYPES_DEFAULT_HEADER = {
        "DEBUG": ("<strong>Debug Mode Enabled!</strong> ", "alert-warning"),
        "UPDATE": ("<strong>Updater:</strong> ", "alert-info"),
        "SEC": ("<strong>Security Issue Detected!</strong> ", "alert-danger"),
    }

    TYPES_DEFAULT_TEXT = {
        "DEBUG": "The unlock functionality has been disabled. Please turn off Debug mode in production.",
        "UPDATE": "<a href=\"https://github.com/kerk12/PiLock\">Update available!</a>",
        "SEC": " "
    }

    # Only one notification created for each type.
    type = models.CharField(max_length=10, choices=TYPES, default="DEBUG", unique=True)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def html(self):
        """ Generates an HTML Bootstrap alert depending on the notification and its text (if it has any). """
        output = ""
        output += '<div class="alert '+ self.TYPES_DEFAULT_HEADER[self.type][1] +'">'
        output += self.TYPES_DEFAULT_HEADER[self.type][0]
        output += self.TYPES_DEFAULT_TEXT[self.type] if not self.text else self.text
        output += '</div>'
        return output