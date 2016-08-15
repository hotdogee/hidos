from __future__ import absolute_import, unicode_literals

from cell.api import TaskViewSet as CellTaskViewSet

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(CellTaskViewSet):
    model = Task
    serializer_class = TaskSerializer
    