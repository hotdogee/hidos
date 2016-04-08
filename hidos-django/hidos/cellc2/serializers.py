from rest_framework import serializers
from rest_framework import filters

from .models import CellC2Task


class CellC2TaskSerializer(serializers.ModelSerializer):
    file = ImageField(write_only=True, max_length=None, allow_empty_file=False, use_url=False)

    class Meta:
        model = CellC2Task
        read_only_fields = ['cell_ratio',
        'user_filename', 'uploaded_type', 'stdout', 'stderr',
        'task_id', 'status', 'dequeued', 'finished', 'user', 'parent_folder', 'version']
        fields = read_only_fields + ['file']
