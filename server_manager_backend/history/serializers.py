from rest_framework import serializers

from history.models import ActionHistory
from server.serializers import ActionSerializer, ServerSerializer


class ActionHistorySerializer(serializers.ModelSerializer):
    action = ActionSerializer(
        read_only=True
    )
    server = ServerSerializer(
        read_only=True
    )

    class Meta:
        model = ActionHistory
        fields = [
            'id',
            'action',
            'server',
            'log',
            'created_at',
            'status'
        ]

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

