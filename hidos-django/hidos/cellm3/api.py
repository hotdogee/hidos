from __future__ import absolute_import, unicode_literals


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
    """
    list
    create
    retrieve
    update
    partial_update
    destroy
     * also delete task folder
    @list_route
    @detail_route
     * move(destination)
    """
    queryset = CellM3Task.objects.all()
    serializer_class = CellM3TaskSerializer
    lookup_field = 'task_id'
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('task_id',)
    pagination_class = None

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.
        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.
        You may want to override this if you need to provide different
        querysets depending on the incoming request.
        (Eg. return a list of items that is specific to the user)
        """
        if self.request.user.username:
            return CellM3Task.objects.filter(user=self.request.user)
        else:
            return CellM3Task.objects.none()

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    @list_route()
    def running(self, request, *args, **kwargs):
        running_tasks = CellM3Task.objects.filter(user=request.user, status__in=['queued', 'running'])
        serializer = self.get_serializer(running_tasks, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):  # CreateModelMixin
        # If anonymous upload, user will be django.contrib.auth.models.AnonymousUser
        # and username will be an empty string.
        task = serializer.save(user=self.request.user)  # returns create model instance
        # put task in queue
        task.enqueue()

        # built-in

        # def create(self, request, *args, **kwargs): # CreateModelMixin
        #     serializer = self.get_serializer(data=request.data)
        #     serializer.is_valid(raise_exception=True)
        #     self.perform_create(serializer)
        #     headers = self.get_success_headers(serializer.data)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # def get_serializer(self, *args, **kwargs): # GenericAPIView
        #     """
        #     Return the serializer instance that should be used for validating and
        #     deserializing input, and for serializing output.
        #     """
        #     serializer_class = self.get_serializer_class()
        #     kwargs['context'] = self.get_serializer_context()
        #     return serializer_class(*args, **kwargs)

        # def get_serializer_context(self): # GenericAPIView
        #     """
        #     Extra context provided to the serializer class.
        #     """
        #     return {
        #         'request': self.request,
        #         'format': self.format_kwarg,
        #         'view': self
        #     }
