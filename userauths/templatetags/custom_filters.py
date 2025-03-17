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

@register.filter(name='get_item')
def get_item(dictionary, key):
    if dictionary is None:
        return {}
    return dictionary.get(key, {})

@register.filter(name='get_schedule')
def get_schedule(schedule, day):
    if not schedule or day not in schedule:
        return {'available': False, 'start': '09:00', 'end': '17:00'}
    return schedule.get(day, {}) 