"""
Definition of forms.
"""

from allauth.account import app_settings as allauth_account_settings
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from users.emails import has_confirmed_email

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        # like the login API (users.serializers.LoginSerializer)
        if (allauth_account_settings.EMAIL_VERIFICATION == allauth_account_settings.EmailVerificationMethod.MANDATORY
                and not has_confirmed_email(user)):
            raise forms.ValidationError(
                _('This email address has not been confirmed yet. Use the link in the confirmation email.'),
                code='unverified')
    username = forms.EmailField(max_length=254,
                                label=_("Email"),
                                widget=forms.EmailInput({
                                    'class': 'form-control',
                                    'autofocus': True,
                                    'placeholder': 'Email'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
