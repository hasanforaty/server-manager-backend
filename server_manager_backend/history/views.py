from django.core.exceptions import BadRequest, ValidationError
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from history.models import ActionHistory, ServerInfo, ServiceHistory, BackupHistory
from history.serializers import ActionHistorySerializer, ServerInfoSerializer, ServiceHistorySerializer, \
    BackupHistorySerializer

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
    queryset = ActionHistory.objects.all().order_by('-created_at')

    def get_queryset(self):
        queryset = self.queryset
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
    queryset = ServerInfo.objects.all().order_by('-created_at')

    def get_queryset(self):
        queryset = self.queryset
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
    queryset = ServiceHistory.objects.all().order_by('-created_at')
    serializer_class = ServiceHistorySerializer

    def get_queryset(self):
        queryset = self.queryset
        service = self.request.query_params.get('service')
        serviceDB = self.request.query_params.get('serviceDB')
        try:
            if service is not None:
                queryset = queryset.filter(service_id=service)
            if serviceDB is not None:
                queryset = queryset.filter(serviceDB_id=serviceDB)
            if serviceDB is not None and service is not None:
                raise ValidationError("serviceDB and service can't both be asked")
        except Exception as ex:
            raise ValidationError(ex)
        return queryset


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='service',
                type=OpenApiTypes.UUID,
                description="id of DB's service backup",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='folder',
                type=OpenApiTypes.UUID,
                description="id of folder backup",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            # OpenApiParameter(
            #     name='check_folder',
            #     type=OpenApiTypes.UUID,
            #     description="id of check folder for  backup",
            #     required=False,
            #     location=OpenApiParameter.QUERY,
            # ),
        ]
    )
)
class BackupHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin
):
    queryset = BackupHistory.objects.all().order_by('-created_at')
    serializer_class = BackupHistorySerializer

    def get_queryset(self):
        queryset = self.queryset
        service = self.request.query_params.get('service')
        folder = self.request.query_params.get('folder')
        # check_folder = self.request.query_params.get('check_folder')
        try:
            if service is not None:
                queryset = queryset.filter(service_id=service)
            if folder is not None:
                queryset = queryset.filter(folder_id=folder)
            # if check_folder is not None:
            #     queryset = queryset.filter(checkFolder_id=check_folder)
            if folder is not None and service is not None:
                raise ValidationError("folder and service can't both be asked")
        except Exception as ex:
            raise ValidationError(ex)
        return queryset
