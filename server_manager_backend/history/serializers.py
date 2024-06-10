from rest_framework import serializers

from history.models import ActionHistory, ServerInfo, ServiceHistory, BackupHistory
from server.serializers import ActionSerializer, ServerSerializer, ServiceSerializer, DBServiceSerializer
from backup.serializers import BackupSerializer


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
        read_only = ['server', 'created_at',]

    # def get_fields(self, *args, **kwargs):
    #     """Make all field read-only"""
    #     fields = super().get_fields()
    #     for field in fields.values():
    #         field.read_only = True
    #     return fields


class ServiceHistorySerializer(serializers.ModelSerializer):
    service = ServiceSerializer(
        read_only=True,
        required=False,
    )
    serviceDB = DBServiceSerializer(
        read_only=True,
        required=False,
    )

    class Meta:
        model = ServiceHistory
        fields = [
            'id',
            'service',
            'serviceDB',
            'type',
            'created_at',
            'status',
        ]


class ServiceServerHistorySerializer(serializers.ModelSerializer):
    service = ServiceSerializer(
        read_only=True
    )

    class Meta:
        model = ServiceHistory
        fields = [
            'id',
            'service',
            'type',
            'created_at',
            'status',
        ]


class ServiceDBHistorySerializer(serializers.ModelSerializer):
    serviceDB = DBServiceSerializer(
        read_only=True
    )

    class Meta:
        model = ServiceHistory
        fields = [
            'id',
            'serviceDB',
            'type',
            'created_at',
            'status'
        ]


class BackupHistorySerializer(serializers.ModelSerializer):
    service = DBServiceSerializer(
        read_only=True,
        required=False,
    )
    folder = BackupSerializer(
        required=False
    )

    class Meta:
        model = BackupHistory
        fields = [
            'id',
            'status',
            'service',
            'folder',
            'type',
            'created_at',
        ]
