import datetime
import uuid

from django.db import models
from django.utils import timezone

from server.models import Server


class FolderBackup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.TextField(default='')
    path = models.TextField()
    destination = models.TextField(blank=True, default='')
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    is_checking = models.BooleanField(default=False)
    pattern = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# class CheckFolderBackup(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
#     name = models.TextField(default='')
#     path = models.TextField()
#     pattern = models.CharField(max_length=64)
#     server = models.ForeignKey(Server, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
