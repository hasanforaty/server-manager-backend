from django.core.exceptions import BadRequest, ValidationError
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from history.models import ActionHistory, ServerInfo
from history.serializers import ActionHistorySerializer, ServerInfoSerializer

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
                type=OpenApiTypes.STR,
                description='id of the server ',
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='action',
                type=OpenApiTypes.STR,
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
                type=OpenApiTypes.STR,
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
