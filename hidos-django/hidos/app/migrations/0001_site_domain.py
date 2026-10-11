"""
Set the django.contrib.sites domain (default example.com) to the real site
domain, hidos.io unless SITE_DOMAIN says otherwise (#78).

allauth uses the Site domain and name in email confirmation and password
reset messages.
"""
from django.conf import settings
from django.db import migrations


def set_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={'domain': settings.SITE_DOMAIN, 'name': settings.SITE_NAME},
    )


def reset_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(id=settings.SITE_ID).update(domain='example.com', name='example.com')


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(set_site_domain, reset_site_domain),
    ]
