from rest_framework import serializers

from history.models import ActionHistory, ServerInfo
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
        """Make all field read-only"""
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields


class ServerInfoSerializer(serializers.ModelSerializer):
    server = ServerSerializer(
        read_only=True
    )

    class Meta:
        model = ServerInfo
        fields = ['id', 'server', 'created_at', 'cpu', 'ram', 'memory']

    def get_fields(self, *args, **kwargs):
        """Make all field read-only"""
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields


