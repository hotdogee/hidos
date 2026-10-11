from django.conf import settings


def site_settings(request):
    """Expose deployment options that templates need."""
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }
