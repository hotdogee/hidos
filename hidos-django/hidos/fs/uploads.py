"""
Chunked resumable uploads (#56).

1. POST   /api/v1/fs/uploads        {"filename": "img.tif", "size": 123456}
                                     -> 201 {"id": ..., "offset": 0, ...}
2. PUT    /api/v1/fs/uploads/<id>   raw bytes of the next chunk, with
                                     Content-Range: bytes <start>-<end>/<size>
                                     -> 200 {"offset": <bytes received>, ...}
   A chunk that does not start at the current offset gets 409 with the
   offset to resume from; GET /api/v1/fs/uploads/<id> returns it as well.
3. When offset == size the upload is complete; create a task from it with
   POST /api/v1/cell/<app>/tasks {"upload": "<id>", "folder": ...}.
   DELETE /api/v1/fs/uploads/<id> aborts an upload.

Chunks must be smaller than DATA_UPLOAD_MAX_MEMORY_SIZE (10 MB by default).
"""
import logging
import os
import re

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import ChunkedUpload

logger = logging.getLogger(__name__)

_content_range = re.compile(r'^bytes (\d+)-(\d+)/(\d+)$')


class ChunkedUploadSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex', read_only=True)
    filename = serializers.CharField(max_length=255)
    size = serializers.IntegerField(min_value=1)
    status = serializers.CharField(read_only=True)
    expires = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ChunkedUpload
        read_only_fields = ['id', 'offset', 'status', 'created', 'completed', 'expires']
        fields = read_only_fields + ['filename', 'size']

    def validate_filename(self, filename):
        return os.path.basename(filename.replace('\\', '/')) or 'upload'

    def validate_size(self, size):
        if size > settings.CHUNKED_UPLOAD_MAX_BYTES:
            raise ValidationError(_('Files must be smaller than %d MB.') % (settings.CHUNKED_UPLOAD_MAX_BYTES // 2 ** 20))
        return size


class ChunkedUploadViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ChunkedUploadSerializer
    throttle_scope = 'upload_chunk'

    def get_queryset(self):
        return ChunkedUpload.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        os.makedirs(settings.CHUNKED_UPLOAD_ROOT, exist_ok=True)
        upload = serializer.save(owner=self.request.user)
        open(upload.path, 'wb').close()
        logger.info('chunked upload %s started by user %s (%d bytes)', upload.id.hex, upload.owner_id, upload.size)

    def perform_destroy(self, instance):
        instance.delete_file()
        instance.delete()

    @action(detail=True, methods=['put'])
    def append(self, request, *args, **kwargs):
        data = request.body
        with transaction.atomic():
            upload = self.get_queryset().select_for_update().get(pk=self.get_object().pk)
            if upload.completed:
                return Response(self.get_serializer(upload).data)
            header = request.headers.get('Content-Range')
            if header:
                match = _content_range.match(header.strip())
                if not match:
                    raise ValidationError({'Content-Range': _('Expected "bytes <start>-<end>/<size>".')})
                start, end, total = (int(g) for g in match.groups())
                if total != upload.size or end < start or end - start + 1 != len(data):
                    raise ValidationError({'Content-Range': _('Does not match the upload size or the chunk length.')})
            else:
                start = upload.offset
            if start != upload.offset:
                return Response(self.get_serializer(upload).data, status=status.HTTP_409_CONFLICT)
            if not data or upload.offset + len(data) > upload.size:
                raise ValidationError({'detail': _('Empty chunk or more data than the declared size.')})
            with open(upload.path, 'r+b' if os.path.exists(upload.path) else 'wb') as fh:
                fh.truncate(upload.offset)  # drop bytes of an interrupted earlier write
                fh.seek(upload.offset)
                fh.write(data)
            upload.offset += len(data)
            if upload.offset == upload.size:
                upload.completed = timezone.now()
            upload.save(update_fields=['offset', 'completed'])
        return Response(self.get_serializer(upload).data)


def take_completed_upload(user, upload_id):
    """Return the finished ChunkedUpload of `user` with id `upload_id`."""
    try:
        upload = ChunkedUpload.objects.get(pk=upload_id, owner=user)
    except (ChunkedUpload.DoesNotExist, ValueError, TypeError):
        raise ValidationError({'upload': _('Upload not found.')})
    if not upload.completed:
        raise ValidationError({'upload': _('Upload is not complete (%d of %d bytes).') % (upload.offset, upload.size)})
    return upload
