import pytz
import datetime
from django import template
from timezones2.utils import get_default_tz, get_current_tz, force_wise

register = template.Library()

@register.filter
def to_current_tz(value):
    if not isinstance(value, datetime.datetime):
        return ''
    value = force_wise(value)
    tz = get_current_tz()
    return value.astimezone(tz)

@register.filter
def to_default_tz(value):
    if not isinstance(value, datetime.datetime):
        return ''
    value = force_wise(value)
    tz = get_default_tz()
    return value.astimezone(tz)

@register.filter
def to_tz(value, arg):
    if not isinstance(value, datetime.datetime):
        return ''
    if isinstance(arg, basestring):
        try:
            arg = pytz.timezone(str(arg))
        except pytz.UnknownTimeZoneError:
            return ''
    value = force_wise(value)
    return value.astimezone(arg)
