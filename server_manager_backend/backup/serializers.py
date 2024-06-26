from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
            'created_at',
            'is_checking',
            'pattern'
        ]


class BackupSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(
        queryset=Server.objects.all(),
    )

    # server = ServerSerializer(read_only=False)
    def validate(self, attrs):
        is_checking = attrs.get('is_checking', False)
        destination = attrs.get('destination', '')
        pattern = attrs.get('pattern', '')
        if (not is_checking) and (not destination):
            raise ValidationError('destination field is required')
        if is_checking and not pattern:
            raise ValidationError('pattern field is required')
        return attrs

    class Meta:
        model = models.FolderBackup
        fields = [
            'id',
            'name',
            'path',
            'destination',
            'server',
            'created_at',
            'is_checking',
            'pattern'
        ]

# class CheckBackupSerializer(serializers.ModelSerializer):
#     server = serializers.PrimaryKeyRelatedField(
#         queryset=Server.objects.all(),
#     )
#
#     class Meta:
#         model = models.CheckFolderBackup
#         fields = [
#             'id',
#             'name',
#             'path',
#             'pattern',
#             'server',
#             'created_at'
#         ]
#
#
# class CheckFolderBackupGetSerializer(serializers.ModelSerializer):
#     server = ServerSerializer(read_only=False)
#
#     class Meta:
#         model = models.CheckFolderBackup
#         fields = '__all__'
