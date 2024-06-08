from rest_framework import mixins, viewsets

from backup.serializers import BackupSerializer
from backup.models import FolderBackup


class FolderBackupViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = BackupSerializer
    queryset = FolderBackup.objects.all()

