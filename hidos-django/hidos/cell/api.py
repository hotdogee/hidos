import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class TaskSubmitRateThrottle(UserRateThrottle):
    """Rate limit for new analysis tasks per user (#26)"""
    scope = 'task_submit'


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
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('id', )
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
        if not self.request.user.is_anonymous:
            return self.model.objects.filter(owner=self.request.user)
        else:
            return self.model.objects.none()

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    def get_throttles(self):
        throttles = super().get_throttles()
        if self.action == 'create':
            throttles.append(TaskSubmitRateThrottle())
        return throttles

    @action(detail=False)
    def running(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        running_tasks = queryset.filter(owner=request.user, status__in=['queued', 'running'])
        serializer = self.get_serializer(running_tasks, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer): # CreateModelMixin
        # Anonymous users are rejected by the IsAuthenticated permission
        task = serializer.save(owner=self.request.user) # returns create model instance
        if getattr(task, 'is_existing', False) and task.status in ('queued', 'running', 'success'):
            # the same image was submitted before, return that task
            return
        if getattr(task, 'is_existing', False):
            # resubmitting an image whose analysis failed runs it again
            task.status, task.progress, task.error = 'queued', 0, ''
            task.save(update_fields=['status', 'progress', 'error', 'modified'])
        # put task in queue
        logger.info('%s: queued task %s for user %s', task.type, task.id.hex, task.owner_id)
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


class ExampleListView(APIView):
    """
    Example input image, result image and numbers of every analysis app
    (#43). Public: the examples are shown before signing in.
    """
    permission_classes = (AllowAny,)
    authentication_classes = ()
    throttle_classes = ()

    def get(self, request, *args, **kwargs):
        from .examples import analysis_apps, example_info
        return Response([info for info in (example_info(c) for c in analysis_apps()) if info])
