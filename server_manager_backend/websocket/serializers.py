from rest_framework import serializers
from server.serializers import ServerSerializer


class ServerSummerySerializer(serializers.ModelSerializer):
    config = ServerSerializer(
        read_only=False,
    )
    info = serializers.JSONField(
        required=True,
        read_only=True
    )
    services = serializers.JSONField(
        read_only=True
    )
    backups = serializers.JSONField(
        read_only=True
    )
