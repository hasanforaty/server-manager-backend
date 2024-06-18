from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError

from server.models import Server, Action, Service, DBService
from server.serializers import ServerSerializer, ActionSerializer, ServiceSerializer, DBServiceSerializer, \
    DBServiceRetrieveSerializer


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
    pagination_class = None


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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="serverId",
                type=OpenApiTypes.UUID,
                description="DB's for that server ",
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
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

    def get_queryset(self):
        queryset = self.queryset
        serverId = self.request.query_params.get('serverId')
        try:
            if serverId is not None:
                queryset = queryset.filter(server_id=serverId)
        except Exception as e:
            raise ValidationError(e)
        return queryset


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="backup",
                type=OpenApiTypes.BOOL,
                description="DB's with backup on ",
                required=False,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="serverId",
                type=OpenApiTypes.UUID,
                description="DB's for that server ",
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
        serverId = self.request.query_params.get('serverId')
        try:
            if is_backup is not None:
                backup = is_backup.lower() == 'true'
                queryset = queryset.filter(backup=backup)
            if serverId is not None:
                queryset = queryset.filter(server_id=serverId)
        except Exception as e:
            raise ValidationError(e)
        return queryset

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve' or self.action == 'list':
            return DBServiceRetrieveSerializer(*args, **kwargs)
        else:
            return DBServiceSerializer(*args, **kwargs)
