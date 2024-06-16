from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from server.models import Server, Action, Service, DBService
from server.serializers import ServerSerializer, ActionSerializer, ServiceSerializer, DBServiceSerializer, \
    DBServiceRetrieveSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter


# Create your views here.

class ServerViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer


class ActionsViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer


class ServiceViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    pagination_class = None


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="backup",
                type=OpenApiTypes.BOOL,
                description="DB's with backup on ",
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class DBServiceViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = DBService.objects.all()
    serializer_class = DBServiceSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = self.queryset
        is_backup = self.request.query_params.get('backup')
        try:
            if is_backup is not None:
                backup = is_backup.lower() == 'true'
                queryset = queryset.filter(backup=backup)
        except Exception as e:
            raise ValidationError(e)
        return queryset

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve' or self.action == 'list':
            return DBServiceRetrieveSerializer(*args, **kwargs)
        else:
            return DBServiceSerializer(*args, **kwargs)
