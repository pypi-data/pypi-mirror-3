import os
import datetime
import pytz
import re
from django.conf import settings
from django.utils.encoding import force_unicode

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

SESSION_KEY = 'timezones2_tz'
_tz_store = local()

_ipv4_private = re.compile(
    r"^(127\.\d{1,3}\.\d{1,3}\.\d{1,3})|"
    r"(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|"
    r"(192\.168\.\d{1,3})\.\d{1,3}|"
    r"(172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})$"
)

def save_tz(request, tz):
    if isinstance(tz, datetime.tzinfo):
        tz = force_unicode(tz)
    request.session[SESSION_KEY] = tz

def activate(tz):
    global _tz_store
    if isinstance(tz, basestring):
        tz = pytz.timezone(str(tz))
    _tz_store.timezone = tz

def deactivate():
    global _tz_store
    if hasattr(_tz_store, 'timezone'):
        del _tz_store.timezone

def get_current_tz():
    tz = getattr(_tz_store, 'timezone', None)
    if tz is None:
        return get_default_tz()
    return tz

def get_default_tz():
    from django.conf import settings
    return pytz.timezone(str(settings.TIME_ZONE))

def force_wise(dt):
    if dt.tzinfo is None:
        default_tz = get_default_tz()
        return default_tz.localize(dt)
    return dt

def ipv4_is_private(ip):
    return _ipv4_private.match(ip)

class GeoTimeZoneReader(object):
    """
    Class for querying timezone.txt file.
    """
    def __init__(self, filename=None):
        if filename is None:
            filename = getattr(settings, 'GEOIP_PATH')
            filename = os.path.join(filename, 'timezone.txt')
        self.filename = filename
        self._load()

    def _load(self):
        fp = open(self.filename)
        data = fp.read().split('\n')
        if data[0].startswith('country'):
            del data[0]
        data = filter(None, data)
        timezones = {}
        for line in data:
            try:
                country, region, timezone = line.split('\t')
            except ValueError:
                try:
                    country, timezone = line.split()
                    region = None
                except ValueError:
                    continue
            
            if not region: region = None
            else: region = region.lower()
            country = country.lower()
            timezones.setdefault(country, {})
            timezones[country][region] = timezone
        self.data = timezones

    def get_timezone(self, country, region=None):
        """
        Returns timezone or None.
        """
        if not region: region = None
        else: region = region.lower()
        country = country.lower()

        if not self.data.has_key(country):
            return None
        country = self.data[country]
        timezone = country.get(region)
        if timezone is None and len(country) > 0:
            timezone = country.values()[0]
        return timezone
