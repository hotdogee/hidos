from __future__ import absolute_import, unicode_literals

from rest_framework import filters
from rest_framework import generics
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import list_route


from .models import Folder, File
from .serializers import FolderSerializer, FileSerializer, FolderFilesSerializer


class FileViewSet(viewsets.ModelViewSet):
    """
    list
    create
    retrieve
    update
    partial_update
    destroy
    """
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('type', 'folder')
    pagination_class = None

    def get_queryset(self): # GenericAPIView
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
            return File.objects.filter(owner=self.request.user)
        else:
            return File.objects.none()

    def perform_create(self, serializer): # CreateModelMixin
        # If anonymous upload, user will be django.contrib.auth.models.AnonymousUser
        # and username will be an empty string.
        obj = serializer.save(owner=self.request.user) # returns create model instance


    @list_route()
    def root(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(folder__isnull=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FolderFilesSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = FolderFilesSerializer(queryset, many=True)

        data = {
            'id': None,
            'type': 'folder',
            'created': None,
            'modified': None,
            'owner': self.request.user.pk,
            'content': {},
            'name': '/',
            'folder': None,
            'breadcrumbs': [],
            'path': '/',
            'files': serializer.data
        }

        return Response(data)


class FolderViewSet(viewsets.ModelViewSet):
    """
    list
    create
    retrieve
    update
    partial_update
    destroy
    @list_route
    @detail_route
     * contents -> retrieve
     * move(destination) -> partial_update
    """
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('folder',)
    pagination_class = None

    def get_queryset(self): # GenericAPIView
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
            return Folder.objects.filter(owner=self.request.user)
        else:
            return Folder.objects.none()

    def perform_create(self, serializer): # CreateModelMixin
        # If anonymous upload, user will be django.contrib.auth.models.AnonymousUser
        obj = serializer.save(owner=self.request.user) # returns create model instance

    # @detail_route()
    # def contents(self, request, pk=None, *args, **kwargs):
    #     folder = self.get_object()
    #     pass

    # @detail_route(methods=['post'])
    # def move(self, request, pk=None, *args, **kwargs):
    #     folder = self.get_object()
    #     pass

    # built-in

    # def filter_queryset(self, queryset): # GenericAPIView
    #     """
    #     Given a queryset, filter it with whichever filter backend is in use.
    #     You are unlikely to want to override this method, although you may need
    #     to call it either from a list view, or from a custom `get_object`
    #     method if you want to apply the configured filtering backend to the
    #     default queryset.
    #     """
    #     for backend in list(self.filter_backends):
    #         queryset = backend().filter_queryset(self.request, queryset, self)
    #     return queryset

    # def get_object(self): # GenericAPIView
    #     """
    #     Returns the object the view is displaying.
    #     You may want to override this if you need to provide non-standard
    #     queryset lookups.  Eg if objects are referenced using multiple
    #     keyword arguments in the url conf.
    #     """
    #     queryset = self.filter_queryset(self.get_queryset())

    #     # Perform the lookup filtering.
    #     lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

    #     assert lookup_url_kwarg in self.kwargs, (
    #         'Expected view %s to be called with a URL keyword argument '
    #         'named "%s". Fix your URL conf, or set the `.lookup_field` '
    #         'attribute on the view correctly.' %
    #         (self.__class__.__name__, lookup_url_kwarg)
    #     )

    #     filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
    #     obj = get_object_or_404(queryset, **filter_kwargs)

    #     # May raise a permission denied
    #     self.check_object_permissions(self.request, obj) # APIView

    #     return obj

    # def retrieve(self, request, *args, **kwargs): # RetrieveModelMixin
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

    # def update(self, request, *args, **kwargs): # UpdateModelMixin
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)

    # def perform_update(self, serializer): # UpdateModelMixin
    #     serializer.save()

    # def partial_update(self, request, *args, **kwargs): # UpdateModelMixin
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)

    # def list(self, request, *args, **kwargs): # ListModelMixin
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    # def perform_create(self, serializer): # CreateModelMixin
    #     # If anonymous user will be django.contrib.auth.models.AnonymousUser
    #     # and username is a empty string.
    #     task = serializer.save(user=self.request.user) # returns create model instance
    #     # put task in queue
    #     task.enqueue()

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
