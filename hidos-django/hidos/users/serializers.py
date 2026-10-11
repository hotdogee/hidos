from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from dj_rest_auth.serializers import JWTSerializer as BaseJWTSerializer

# Get the UserModel
UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = authenticate(self.context.get('request'), email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = self._validate_email(email, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'dj_rest_auth.registration' in settings.INSTALLED_APPS:
            if allauth_account_settings.EMAIL_VERIFICATION == allauth_account_settings.EmailVerificationMethod.MANDATORY:
                if not user.emailaddress_set.filter(email__iexact=user.email, verified=True).exists():
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs


class TokenClaimsSerializer(TokenObtainPairSerializer):
    """
    JWT claims. The token identifies the user by id; email and full_name are
    included for clients (the username is not, see #95).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        return token


class JWTSerializer(BaseJWTSerializer):
    """
    Serializer for JWT authentication.
    `token` is the access token, kept for clients written against the
    djangorestframework-jwt API; `access`, `refresh` and `user` are new.
    """
    token = serializers.CharField(source='access', read_only=True)


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password, including the profile fields (#75)
    """
    image = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = UserModel
        read_only_fields = ('email', 'is_staff', 'is_active', 'date_joined', 'last_login', 'get_full_name', 'get_short_name')
        fields = ('first_name', 'last_name', 'organization', 'language', 'image') + read_only_fields

    def validate_language(self, language):
        if language and language not in dict(settings.LANGUAGES):
            raise serializers.ValidationError(
                _('Unsupported language. Choose one of: %s') % ', '.join(dict(settings.LANGUAGES)))
        return language

    def validate_image(self, image):
        if image and image.size > settings.PROFILE_IMAGE_MAX_BYTES:
            raise serializers.ValidationError(
                _('Profile images must be smaller than %d KB.') % (settings.PROFILE_IMAGE_MAX_BYTES // 1024))
        return image


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=False, max_length=150,
        style={'placeholder': '(Optional)'}
    )
    last_name = serializers.CharField(
        required=False, max_length=150,
        style={'placeholder': '(Optional)'}
    )
    email = serializers.EmailField(
        required=True, write_only=True
    )
    password1 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and (UserModel.objects.filter(email__iexact=email).exists()
                      or EmailAddress.objects.filter(email__iexact=email).exists()):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
