# Lower-case the addresses that UserManager.normalize_email stored with
# upper-case letters before the @ (#67).

from django.db import migrations


def lower_case_emails(apps, schema_editor):
    """
    allauth's account.0006 lower-cased every address once; since then,
    accounts from createsuperuser or the admin kept the case of the part
    before the @. An address whose lower-cased form another account already
    has (or that wouldn't fit) is left alone.
    """
    User = apps.get_model('users', 'User')
    users = User.objects.using(schema_editor.connection.alias)
    max_length = User._meta.get_field('email').max_length
    accounts = list(users.values_list('pk', 'email'))
    taken = {email for pk, email in accounts}
    for pk, email in accounts:
        lower = email.lower()
        if lower != email and lower not in taken and len(lower) <= max_length:
            users.filter(pk=pk).update(email=lower)
            taken.add(lower)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_profile'),
    ]

    operations = [
        migrations.RunPython(lower_case_emails, migrations.RunPython.noop),
    ]
