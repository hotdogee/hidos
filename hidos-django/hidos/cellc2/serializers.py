from rest_framework import serializers
from rest_framework import filters

from .models import CellC2Task


class CellC2TaskSerializer(serializers.ModelSerializer):


    class Meta:
        model = CellC2Task
        fields = ('cell_ratio', 
        'user_filename', 'uploaded_type', 'stdout', 'stderr', 
        'task_id', 'status', 'dequeued', 'finished', 'user', 'parent_folder', 'version')
        read_only_fields = fields