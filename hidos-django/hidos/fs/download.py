"""
Batch result download (#35): one zip with the result image of every selected
task (optionally the uploaded image too) and a results.csv with the numbers.
"""
import csv
import io
import json
import re
import tempfile
import uuid
import zipfile
from os import path

from django.http import FileResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

MAX_FILES = 2000
_unsafe = re.compile(r'[\\/:*?"<>|\x00-\x1f]+')


def safe_name(name):
    return _unsafe.sub('_', name).strip(' .') or '_'


def collect_tasks(queryset, ids):
    """Resolve ids (hex) owned by the user into (zip folder, task) pairs."""
    try:
        uuids = [uuid.UUID(str(i)) for i in ids]
    except (TypeError, ValueError, AttributeError):
        raise ValidationError({'ids': _('Invalid id.')})
    if not uuids:
        raise ValidationError({'ids': _('Select at least one file or folder.')})
    tasks = []
    seen = set()
    stack = [(f, '') for f in queryset.filter(id__in=uuids)]
    while stack:
        f, prefix = stack.pop()
        if f.id in seen:
            continue
        seen.add(f.id)
        if f.type == 'folder':
            sub = prefix + safe_name(f.name) + '/'
            stack.extend((child, sub) for child in queryset.filter(folder_id=f.id))
        elif hasattr(f.content, 'result_image'):
            tasks.append((prefix, f.content))
        if len(tasks) > MAX_FILES:
            raise ValidationError({'ids': _('Too many files, select at most %d.') % MAX_FILES})
    return tasks


def _add(zf, field, arcname):
    if field and path.isfile(field.path):
        zf.write(field.path, arcname)
        return True
    return False


def zip_response(queryset, ids, include_uploaded=False):
    tasks = collect_tasks(queryset, ids)
    result_keys = []
    for _prefix, task in tasks:
        for key in (task.result or {}):
            if key not in result_keys:
                result_keys.append(key)

    out = tempfile.SpooledTemporaryFile(max_size=64 * 1024 * 1024)
    rows = io.StringIO()
    writer = csv.writer(rows)
    writer.writerow(['path', 'name', 'id', 'app', 'version', 'status', 'created', 'finished'] + result_keys)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_STORED) as zf:
        used = set()
        for prefix, task in tasks:
            stem = prefix + safe_name(path.splitext(task.name)[0]) + '_' + task.id.hex[:6]
            while stem in used:
                stem += '_'
            used.add(stem)
            ext = path.splitext(task.result_image.name)[1] if task.result_image else ''
            result_path = stem + '_result' + ext
            if not _add(zf, task.result_image, result_path):
                result_path = ''
            if include_uploaded and task.uploaded_image:
                _add(zf, task.uploaded_image, stem + '_uploaded' + path.splitext(task.uploaded_image.name)[1])
            result = task.result or {}
            writer.writerow([result_path, task.name, task.id.hex, task.type, task.version, task.status,
                             task.created.isoformat() if task.created else '',
                             task.finished.isoformat() if task.finished else ''] +
                            [json.dumps(result[k]) if isinstance(result.get(k), (dict, list)) else result.get(k, '')
                             for k in result_keys])
        zf.writestr('results.csv', rows.getvalue())
    out.seek(0)
    return FileResponse(out, as_attachment=True, filename='cell-cloud-results.zip',
                        content_type='application/zip')
