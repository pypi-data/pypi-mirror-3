from django import forms
from timezones2.utils import get_current_tz

class DateTimeField2(forms.DateTimeField):
    def clean(self, value):
        value = super(DateTimeField2, self).clean(value)
        if value is None:
            return value
        if value.tzinfo is None:
            tz = get_current_tz()
            value = tz.localize(value)
        return value
