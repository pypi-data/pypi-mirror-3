from django import http
from django.conf import settings

from daycare.models import Redirect


class RedirectFallbackMiddleware(object):
    """
    Redirecting middleware. The code is pretty much based
    on django.contrib.redirects.middleware.RedirectFallbackMiddleware.

    As it's fallback it should be on top of MIDDLEWARE_CLASSES setting.
    """
    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a redirect for non-404 responses.
        path = request.path  # FIXME: we should this WSGIScriptAlias aware (path_info stuff)
        try:
            r = Redirect.objects.get(catch_url=path, status=Redirect.STATUS_ACTIVE)
        except Redirect.DoesNotExist:
            r = None
        if r is None and settings.APPEND_SLASH:
            # Try removing the trailing slash.
            try:
                r = Redirect.objects.get(catch_url=path[:-1])
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            if r.redirect_url == '':
                return http.HttpResponseGone()
            return http.HttpResponsePermanentRedirect(r.redirect_url)

        # No redirect was found. Return the response.
        return response
