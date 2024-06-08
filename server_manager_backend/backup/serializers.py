from rest_framework import serializers

from backup import models
from server.models import Server


class BackupSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(
        queryset=Server.objects.all(),
    )

    class Meta:
        model = models.FolderBackup
        fields = [
            'id',
            'path',
            'destination',
            'server',
            'created_at'
        ]
