from django import template
from PiLock.settings import getServerVersion
register = template.Library()

@register.simple_tag
def datetime_to_str(obj):
    return str(obj.datetime)

@register.simple_tag
def get_version():
    return "PiLock Server v." + getServerVersion()