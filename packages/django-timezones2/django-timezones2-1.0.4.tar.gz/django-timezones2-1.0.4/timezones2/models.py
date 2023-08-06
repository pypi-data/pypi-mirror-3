import pytz
from django.db import models, connection as default_connection
from django.utils.encoding import smart_unicode, smart_str
from timezones2.utils import get_default_tz, get_current_tz, force_wise
from timezones2 import forms, zones

try:
    import MySQLdb
    HAS_MYSQLDB_MODULE = True
    from django.db.backends.mysql.base import DatabaseWrapper as MysqlDatabaseWrapper
except ImportError:
    MysqlDatabaseWrapper = None
    HAS_MYSQLDB_MODULE = False

class TimeZoneField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 64,
            'choices': zones.CHOICES_COMMON
        }
        defaults.update(kwargs)
        super(TimeZoneField, self).__init__(*args, **defaults)

    def to_python(self, value):
        value = super(TimeZoneField, self).to_python(value)
        if isinstance(value, basestring) and value: # don't accept empty strings
            value = pytz.timezone(str(value))
        return value

    def get_db_prep_value(self, value, *args, **kwargs):
        value = super(TimeZoneField, self).get_db_prep_value(value, *args, **kwargs)
        if value is not None:
            value = smart_unicode(value)
        return value

    def validate(self, value, model_instance):
        value = smart_str(value)
        super(TimeZoneField, self).validate(value, model_instance)

    def run_validators(self, value):
        value = smart_str(value)
        super(TimeZoneField, self).run_validators(value)

class DateTimeField2(models.DateTimeField):
    __metaclass__ = models.SubfieldBase

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        if connection is None:
            connection = default_connection

        if not (value is None or self.db_supports_timezones(connection)):
            value = value.replace(tzinfo=None)

        return connection.ops.value_to_db_datetime(value)

    def get_prep_value(self, value):
        default_tz = get_default_tz()
        if value is not None:
            if value.tzinfo is None:
                value = default_tz.localize(value)
            else:
                value = value.astimezone(default_tz)
        return value

    def to_python(self, value):
        # parse string, so loaddata will work
        value = super(DateTimeField2, self).to_python(value)
        if value is not None:
            value = force_wise(value)
            tz = get_current_tz()
            value = value.astimezone(tz)
        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.DateTimeField2}
        defaults.update(kwargs)
        return super(DateTimeField2, self).formfield(**defaults)

    def db_supports_timezones(self, connection):
        if hasattr(connection.features, "supports_timezones"):
            return connection.features.supports_timezones # django 1.3+
        else:
            return HAS_MYSQLDB_MODULE and not isinstance(connection, MysqlDatabaseWrapper)
