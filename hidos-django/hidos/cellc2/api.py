
from rest_framework import filters
from rest_framework import generics
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response

from .models import CellC2Task
from .serializers import CellC2TaskSerializer

class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = CellC2Task.objects.all()
    serializer_class = CellC2TaskSerializer
    lookup_field = 'task_id'
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('task_id', )
    pagination_class = None
