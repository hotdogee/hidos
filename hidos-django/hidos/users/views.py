from dj_rest_auth.registration.views import RegisterView as BaseRegisterView


class RegisterView(BaseRegisterView):
    """
    Local account signup (#18). Registration has its own, stricter throttle
    than the other dj-rest-auth views.
    """
    throttle_scope = 'register_view'
