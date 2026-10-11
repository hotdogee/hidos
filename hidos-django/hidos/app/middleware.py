from .views import healthz


class HealthCheckMiddleware:
    """
    Answer /healthz before Django validates the Host header or redirects to
    HTTPS, so the container health check (http://127.0.0.1:8000/healthz)
    works whatever DJANGO_ALLOWED_HOSTS and SECURE_SSL_REDIRECT are.
    Must be the first middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info == '/healthz':
            return healthz(request)
        return self.get_response(request)
