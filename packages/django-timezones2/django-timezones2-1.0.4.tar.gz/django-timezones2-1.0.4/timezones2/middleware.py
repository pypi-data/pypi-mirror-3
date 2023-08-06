import pytz
from django.conf import settings
from django.contrib.gis.utils.geoip import GeoIP, GeoIPException
from django.core.exceptions import ImproperlyConfigured
from timezones2.utils import activate, deactivate, GeoTimeZoneReader, ipv4_is_private

SESSION_KEY = 'timezones2_tz'

class TimezonesMiddleware(object):
    def get_timezone(self, request):
        return None

    def process_request(self, request):
        tz = self.get_timezone_from_request(request)
        tz = pytz.timezone(str(tz))
        activate(tz)

    def process_response(self, request, response):
        deactivate()
        return response

    def get_timezone_from_request(self, request):
        # get timezone from session
        tz = request.session.get(SESSION_KEY)
        if tz is not None:
            return tz

        # use custom handler to retrieve timezone
        # (you may override this middleware and provide one)
        tz = self.get_timezone(request)

        # try using geoIP database
        if tz is None and getattr(settings, "TZ2_USE_GEOIP", False):
            tz = self.get_timezone_from_geoip(request)

        # fallback to default timezone
        if tz is None:
            tz = getattr(settings, "TIME_ZONE", "UTC")

        request.session[SESSION_KEY] = tz
        return tz
    
    def get_timezone_from_geoip(self, request):
        try:
            g = GeoIP()
        except GeoIPException, e:
            raise ImproperlyConfigured(e.args[0])

        # don't perform query against ipv4 private subnets
        query = request.META['REMOTE_ADDR']
        if ipv4_is_private(query):
            return
        
        result = g.city(query)
        if not result:
            return
        
        db = GeoTimeZoneReader()
        return db.get_timezone(result.get('country_code'), result.get('region'))
