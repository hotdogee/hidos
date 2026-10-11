import uuid
from os import path

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        """
        Lower-cases the whole address, not only the domain (#67): allauth
        stores addresses lower-cased and looks them up exactly, so it took
        Root@example.com, e.g. from createsuperuser or the admin, for
        another address than root@example.com.
        """
        return super().normalize_email(email).lower()

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user( email, password, **extra_fields)

def user_image_path(instance, filename):
    """Profile images are stored under a random name, never the uploaded one."""
    ext = path.splitext(filename)[1].lower()[:10]
    return 'users/images/{0}{1}'.format(uuid.uuid4().hex, ext)


class User(AbstractUser):
    """
    Email and password are required. Other fields are optional.
    The email address is the account name (#74).
    """
    username_validator = None
    username = None

    email = models.EmailField(
        _('email address'), 
        unique=True,
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    # Profile (#74)
    image = models.ImageField(_('profile image'), upload_to=user_image_path, max_length=255, blank=True)
    organization = models.CharField(_('organization'), max_length=255, blank=True)
    language = models.CharField(_('language'), max_length=10, blank=True, default='en',
        help_text=_('Preferred interface language, one of settings.LANGUAGES.'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        name = ('%s %s' % (self.first_name, self.last_name)).strip()
        if not name:
            name = self.email.split('@')[0]
        return name

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        name = self.first_name
        if not name:
            name = self.email.split('@')[0]
        return name