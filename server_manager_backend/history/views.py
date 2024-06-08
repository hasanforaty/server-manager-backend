from rest_framework import mixins,viewsets

from history.models import ActionHistory
from history.serializers import ActionHistorySerializer


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

