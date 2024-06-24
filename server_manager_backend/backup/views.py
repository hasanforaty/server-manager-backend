from rest_framework import mixins, viewsets

from backup.serializers import BackupSerializer, BackupGetSerializer
from backup.models import FolderBackup


class FolderBackupViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BackupSerializer
    queryset = FolderBackup.objects.all()
    pagination_class = None

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve' or self.action == 'list':
            return BackupGetSerializer(*args, **kwargs)
        else:
            return BackupSerializer(*args, **kwargs)


# class CheckFolderBackupViewSet(
#     mixins.CreateModelMixin,
#     mixins.DestroyModelMixin,
#     mixins.ListModelMixin,
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     viewsets.GenericViewSet,
#
# ):
#     serializer_class = CheckBackupSerializer
#     queryset = CheckFolderBackup.objects.all()
#     pagination_class = None
#
#     def get_serializer(self, *args, **kwargs):
#         if self.action == 'retrieve' or self.action == 'list':
#             return CheckFolderBackupGetSerializer(*args, **kwargs)
#         else:
#             return CheckBackupSerializer(*args, **kwargs)
