from rest_framework import mixins, viewsets

from history.models import ActionHistory
from history.serializers import ActionHistorySerializer

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
                description='id of The server ',
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
        if server is not None:
            queryset = queryset.filter(server_id=server)
        action = self.request.query_params.get('action')
        if action is not None:
            queryset = queryset.filter(action_id=action)
        return queryset
