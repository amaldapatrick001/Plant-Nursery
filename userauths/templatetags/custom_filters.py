from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """
    Splits a string into a list using the specified delimiter
    Usage: {{ value|split:"," }}
    """
    if value:
        return [x.strip() for x in value.split(arg)]
    return []

@register.filter(name='strip')
def strip(value):
    """
    Strips whitespace from a string
    Usage: {{ value|strip }}
    """
    if value:
        return value.strip()
    return '' 