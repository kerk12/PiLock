from django import template

register = template.Library()

@register.simple_tag
def datetime_to_str(obj):
    return str(obj.datetime)