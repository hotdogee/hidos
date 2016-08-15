from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

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

class User(AbstractUser):
    """
    Email and password are required. Other fields are optional.
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