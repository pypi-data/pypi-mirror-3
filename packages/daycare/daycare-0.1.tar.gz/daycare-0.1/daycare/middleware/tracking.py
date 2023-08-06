from datetime import date
from django import http
from django.conf import settings

from daycare.models import MissingURL, URLHit


class Track404sMiddleware:
    """
    Store all 404s and number of hits for each one.

    Should stay close to bottom of MIDDLEWARE_CLASSES settings to be sure
    it catches all 404s.
    """
    def process_exception(self, request, exception):
        if type(exception) == http.Http404:
            # first make it slash-proof
            path_slashless = request.path
            if settings.APPEND_SLASH and request.path.endswith('/'):
                path_slashless = request.path[:-1]
            if request.path not in getattr(settings, 'DAYCARE_DONT_TRACK_URLS', []) \
            and path_slashless not in getattr(settings, 'DAYCARE_DONT_TRACK_URLS', []):
                url_object, created = MissingURL.objects.get_or_create(url=request.path)
                url_object.save()
                URLHit(url=url_object).save()
