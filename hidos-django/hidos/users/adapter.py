from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MaxLengthValidator

from .emails import has_ascii_local_part, same_email


class AccountAdapter(DefaultAccountAdapter):
    """
    clean_email refuses addresses that allauth would store as another one
    (cut to fit User.email) or that can't be mailed (users.emails). Signups,
    added addresses, password resets and social logins all go through it.

    An address that an account added under /accounts/email/ is only confirmed
    by that account (#67): the link has to be opened while logged in as it.
    The account's own address (user.email, the one it signed up with) is
    still confirmed by the link alone. (An account without a confirmed
    address may make an added one its own address, but that gets it no more
    than signing up with that address would.)

    The mail and the page behind the link name the account that asked by its
    address, and nothing in them shows that victim@gmaıl.com isn't the
    reader's own victim@gmail.com. Whoever owns such a look-alike could add
    victim@gmail.com to it and have the victim confirm it with one click;
    SocialAccountAdapter would then merge the victim's Google logins into the
    look-alike account, whose owner keeps its password. A victim who had
    signed up but not confirmed yet couldn't confirm their own account any
    more, either.
    """

    def clean_email(self, email):
        email = super().clean_email(email)
        stored = email.lower()  # as allauth stores and mails it
        if not has_ascii_local_part(stored):
            raise ValidationError(EmailValidator.message, code=EmailValidator.code)
        # allauth would cut a longer one to fit User.email, i.e. register and mail another address;
        # str.lower() can make an address longer (it turns İ into i and a combining dot)
        MaxLengthValidator(EmailAddress._meta.get_field('email').max_length)(stored)
        return email

    def send_mail(self, template_prefix, email, context):
        # such an address, stored before clean_email refused them, can't be mailed (users.emails)
        if has_ascii_local_part(email):
            super().send_mail(template_prefix, email, context)

    def confirm_email(self, request, email_address):
        if (not same_email(email_address.email, email_address.user.email)
                and request.user.pk != email_address.user_id):
            return False
        return super().confirm_email(request, email_address)

    def get_email_verification_redirect_url(self, email_address):
        if not email_address.verified and not self.request.user.is_authenticated:
            # not confirmed: log in, then back to the link (e.g. opened on another device)
            return redirect_to_login(self.request.get_full_path())['Location']
        return super().get_email_verification_redirect_url(email_address)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Social logins are merged into the local account with the same email (#67),
    but only into an account that has confirmed that address.

    allauth also merges into accounts that merely hold the address
    unconfirmed, and only wipes their password. Whoever created such an
    account (a local signup or a Facebook login with someone else's email,
    or a second address added under /accounts/email/) would keep access
    through their other social logins, addresses and password resets, and
    the person signing in with Google would end up in their account. An
    address added to an account is only confirmed by that account itself
    (AccountAdapter).

    The addresses must be the same under ASCII-only case folding
    (users.emails): iexact on PostgreSQL also takes victim@gmaıl.com, a
    mailbox at another domain, for victim@gmail.com.
    """

    def authenticate_by_email(self, sociallogin):
        for email in [e.email for e in sociallogin.email_addresses if e.verified]:
            if not self.can_authenticate_by_email(sociallogin, email):
                continue
            users = {address.user for address in
                     EmailAddress.objects.filter(email__iexact=email, verified=True).select_related('user')
                     if same_email(address.email, email)}
            if len(users) == 1:
                return users.pop(), email
        return None
