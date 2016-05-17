
from rest_framework import filters
from rest_framework import generics
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import list_route


from .models import CellM3Task
from .serializers import CellM3TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = CellM3Task.objects.all()
    serializer_class = CellM3TaskSerializer
    lookup_field = 'task_id'
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('task_id', )
    pagination_class = None

    @list_route()
    def running(self, request, *args, **kwargs):
        running_tasks = CellC1Task.objects.filter(user=request.user, status__in=['queued', 'running'])
        serializer = self.get_serializer(running_tasks, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # If anonymous user will be django.contrib.auth.models.AnonymousUser
        # and username is a empty string.
        task = serializer.save(user=self.request.user) # returns create model instance
        # put task in queue
        task.enqueue()

    # built-in

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def get_serializer(self, *args, **kwargs):
    #     """
    #     Return the serializer instance that should be used for validating and
    #     deserializing input, and for serializing output.
    #     """
    #     serializer_class = self.get_serializer_class()
    #     kwargs['context'] = self.get_serializer_context()
    #     return serializer_class(*args, **kwargs)

    # def get_serializer_context(self):
    #     """
    #     Extra context provided to the serializer class.
    #     """
    #     return {
    #         'request': self.request,
    #         'format': self.format_kwarg,
    #         'view': self
    #     }
