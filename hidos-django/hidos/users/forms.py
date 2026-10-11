"""
allauth and dj-rest-auth forms that know whose an address is (#67), in
ACCOUNT_FORMS and REST_AUTH (users.serializers.PasswordResetSerializer).

An account can add addresses that aren't its own under /accounts/email/,
so holding an address shows nothing. It is owned by the account whose own
address (user.email) or confirmed address it is (users.emails.email_owners).
"""
from allauth.account.adapter import get_adapter
from allauth.account.forms import AddEmailForm as BaseAddEmailForm
from allauth.account.forms import ResetPasswordForm as BaseResetPasswordForm
from dj_rest_auth.forms import AllAuthPasswordResetForm

from .emails import email_owners


class AddEmailForm(BaseAddEmailForm):
    """
    An address that another account owns can't be added. An account without
    a confirmed address may make an added address its own (user.email,
    which is unique): that was an IntegrityError, and with an address
    stored with other upper-case letters (createsuperuser) a takeover of
    that account's Google logins.
    """

    def clean_email(self):
        email = super().clean_email()
        if any(owner.pk != self.user.pk for owner in email_owners(email)):
            raise get_adapter().validation_error('email_taken')
        return email


class OwnersOnlyMixin:
    """
    Password reset links are only mailed for the accounts that own the
    address. allauth (unless one has confirmed it) and dj-rest-auth also
    mail one for every account that merely added it.
    """

    def clean_email(self):
        email = super().clean_email()
        owners = email_owners(email)
        self.users = [user for user in self.users if user in owners]
        return email


class ResetPasswordForm(OwnersOnlyMixin, BaseResetPasswordForm):
    """/accounts/password/reset/"""


class PasswordResetForm(OwnersOnlyMixin, AllAuthPasswordResetForm):
    """/api/v1/auth/password/reset/"""
