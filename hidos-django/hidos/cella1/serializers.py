from __future__ import absolute_import, unicode_literals

from rest_framework import serializers
from rest_framework import filters

from cell.serializers import TaskSerializer as CellTaskSerializer

from .models import Task


class TaskSerializer(CellTaskSerializer):

    class Meta(CellTaskSerializer.Meta):
        model = Task
