"""
Delete chunked uploads older than CHUNKED_UPLOAD_EXPIRATION (24 hours by
default), finished or not, with their data (#56). Run it from cron, e.g.

    docker compose exec web python manage.py cleanup_uploads
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from fs.models import ChunkedUpload


class Command(BaseCommand):
    help = 'Delete expired chunked uploads and their data.'

    def handle(self, *args, **options):
        expired = ChunkedUpload.objects.filter(created__lt=timezone.now() - settings.CHUNKED_UPLOAD_EXPIRATION)
        count = 0
        for upload in expired:
            upload.delete_file()
            upload.delete()
            count += 1
        self.stdout.write('Deleted %d expired upload(s).' % count)
