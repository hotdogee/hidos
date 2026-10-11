import re
from django import http
from django.conf import settings
from django.urls import is_valid_path
from django.core.exceptions import ImproperlyConfigured


class RemoveSlashMiddleware(object):
    """
    This middleware provides the inverse of the APPEND_SLASH option built into
    django.middleware.common.CommonMiddleware. It should be placed just before
    or just after CommonMiddleware.
    """

    response_redirect_class = http.HttpResponsePermanentRedirect

    def process_request(self, request):

        old_url = request.get_full_path()
        # match any / followed by ? (query string present)
        # OR match / at the end of the string (no query string)
        trailing_slash_regexp = r'(\/(?=\?))|(\/$)'
        new_url = old_url

        if getattr(settings, 'APPEND_SLASH') and getattr(settings, 'REMOVE_SLASH'):
            raise ImproperlyConfigured("APPEND_SLASH and REMOVE_SLASH may not both be True.")

        # Remove slash if REMOVE_SLASH is set and the URL has a trailing slash
        # and there is no pattern for the current path
        if getattr(settings, 'REMOVE_SLASH', False) and re.search(trailing_slash_regexp, old_url):
            urlconf = getattr(request, 'urlconf', None)
            if (not is_valid_path(request.path_info, urlconf)) and is_valid_path(request.path_info[:-1], urlconf):
                new_url = re.sub(trailing_slash_regexp, '', old_url)
                if settings.DEBUG and request.method == 'POST':
                    raise RuntimeError((""
                    "You called this URL via POST, but the URL ends in a "
                    "slash and you have REMOVE_SLASH set. Django can't "
                    "redirect to the non-slash URL while maintaining POST "
                    "data. Change your form to point to %s (without a "
                    "trailing slash), or set REMOVE_SLASH=False in your "
                    "Django settings.") % (new_url))

        if new_url != old_url:
            return self.response_redirect_class(new_url)
        