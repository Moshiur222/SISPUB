from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='split')
@stringfilter
def split(value, key):
    
    try:
        return value.split(key)
    except (ValueError, AttributeError):
        return [value]

@register.filter(name='wordcount')
def wordcount(value):

    try:
        return len(value.split())
    except (ValueError, AttributeError):
        return 0