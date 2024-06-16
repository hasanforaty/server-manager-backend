import uuid

from django.db import models

from server.models import Server


class FolderBackup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    name = models.TextField(default='')
    path = models.TextField()
    destination = models.TextField()
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
