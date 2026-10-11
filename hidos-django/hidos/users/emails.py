"""
Comparing email addresses (#67).

Two addresses are the same only if they are equal after lower-casing the
ASCII letters A-Z, and nothing else. Mail to such addresses goes to the same
domain (DNS ignores ASCII case) and, as mail providers ignore the case of
the local part too (allauth stores addresses lower-cased anyway), to the same
mailbox: confirming one confirms the other.

Unicode case mapping doesn't have that property. PostgreSQL's UPPER(), which
Django's iexact uses, turns the dotless i in victim@gmaıl.com into an ASCII
I, so iexact takes it for victim@gmail.com, although mail to it goes to
xn--gmal-nza.com, a domain anyone can register. Python's str.lower() turns
the Kelvin sign U+212A into an ASCII k. Database lookups may narrow down the
candidates with iexact (it never misses an address that is the same under
this rule); the comparison itself is done here.
"""
import string

_ASCII_LOWER = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)


def email_key(email):
    return (email or '').translate(_ASCII_LOWER)


def same_email(a, b):
    return bool(a) and email_key(a) == email_key(b)


def has_confirmed_email(user):
    """Whether the user confirmed the account's own address (user.email)."""
    return any(same_email(address.email, user.email)
               for address in user.emailaddress_set.filter(verified=True))
