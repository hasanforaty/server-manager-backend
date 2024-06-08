from django.core.exceptions import BadRequest, ValidationError
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from history.models import ActionHistory, ServerInfo, ServiceHistory
from history.serializers import ActionHistorySerializer, ServerInfoSerializer, ServiceHistorySerializer

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='server',
                type=OpenApiTypes.UUID,
                description='id of the server ',
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='action',
                type=OpenApiTypes.UUID,
                description='id of the action in history',
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
)
class ActionHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ActionHistorySerializer
    queryset = ActionHistory.objects.all()

    def get_queryset(self):
        queryset = ActionHistory.objects.all()
        server = self.request.query_params.get('server')
        try:
            if server is not None:
                queryset = queryset.filter(server_id=server)
            action = self.request.query_params.get('action')
            if action is not None:
                queryset = queryset.filter(action_id=action)
        except Exception as e:
            raise ValidationError(e)
        return queryset


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='server',
                type=OpenApiTypes.UUID,
                description='id of the server ',
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
)
class ServerInfoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ServerInfoSerializer
    queryset = ServerInfo.objects.all()

    def get_queryset(self):
        queryset = ServerInfo.objects.all()
        server = self.request.query_params.get('server')
        if server is not None:
            try:
                queryset = queryset.filter(server_id=server)
            except Exception as er:
                raise ValidationError(er)
        return queryset


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='service',
                type=OpenApiTypes.UUID,
                description="id of server's Service",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='serviceDB',
                type=OpenApiTypes.UUID,
                description="id of database's Service",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
)
class ServiceHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = ServiceHistory.objects.all()
    serializer_class = ServiceHistorySerializer

    def get_queryset(self):
        queryset = ServiceHistory.objects.all()
        service = self.request.query_params.get('service')
        serviceDB = self.request.query_params.get('serviceDB')
        try:
            if service is not None:
                queryset = queryset.filter(service_id=service)
            if serviceDB is not None:
                queryset = queryset.filter(serviceDB_id=serviceDB)
        except Exception as ex:
            raise ValidationError(ex)
        return queryset
