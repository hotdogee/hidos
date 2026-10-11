from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Social logins are merged into the local account with the same email (#67),
    but only into an account that has confirmed that address.

    allauth also merges into accounts that merely hold the address
    unconfirmed, and only wipes their password. Whoever created such an
    account (a local signup or a Facebook login with someone else's email,
    or a second address added under /accounts/email/) would keep access
    through their other social logins, addresses and password resets, and
    the person signing in with Google would end up in their account.
    """

    def authenticate_by_email(self, sociallogin):
        for email in [e.email for e in sociallogin.email_addresses if e.verified]:
            if not self.can_authenticate_by_email(sociallogin, email):
                continue
            users = {address.user for address in
                     EmailAddress.objects.filter(email__iexact=email, verified=True).select_related('user')}
            if len(users) == 1:
                return users.pop(), email
        return None
