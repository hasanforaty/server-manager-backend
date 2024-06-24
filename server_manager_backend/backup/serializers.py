from rest_framework import serializers

from backup import models
from server.models import Server
from server.serializers import ServerSerializer


class BackupGetSerializer(serializers.ModelSerializer):
    # server = serializers.PrimaryKeyRelatedField(
    #     queryset=Server.objects.all(),
    # )
    server = ServerSerializer(read_only=False)

    class Meta:
        model = models.FolderBackup
        fields = [
            'id',
            'name',
            'path',
            'destination',
            'server',
            'created_at'
        ]


class BackupSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(
        queryset=Server.objects.all(),
    )

    # server = ServerSerializer(read_only=False)

    class Meta:
        model = models.FolderBackup
        fields = [
            'id',
            'name',
            'path',
            'destination',
            'server',
            'created_at'
        ]


class CheckBackupSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(
        queryset=Server.objects.all(),
    )

    class Meta:
        model = models.CheckFolderBackup
        fields = [
            'id',
            'name',
            'path',
            'pattern',
            'server',
            'created_at'
        ]


class CheckFolderBackupGetSerializer(serializers.ModelSerializer):
    server = ServerSerializer(read_only=False)

    class Meta:
        model = models.CheckFolderBackup
        fields = '__all__'
