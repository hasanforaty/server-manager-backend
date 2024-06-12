import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from django.forms import JSONField

from server.models import Action, Server, Service, DBService
from backup.models import FolderBackup


class ActionHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    action = models.ForeignKey(Action, on_delete=models.SET_NULL, null=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, )
    log = models.JSONField(null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True, null=True, blank=True)


class ServerInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True, editable=False)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True)
    cpu = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    ram = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    memory = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    log = models.JSONField(null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)


class ServiceHistory(models.Model):
    TYPE_CHOICES = (
        ('server', 'Server'),
        ('service', 'Service')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    service = models.ForeignKey(Service, blank=True, null=True, on_delete=models.SET_NULL)
    serviceDB = models.ForeignKey(DBService, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(
        null=False,
        choices=TYPE_CHOICES,
        max_length=32,
    )
    status = models.BooleanField(default=True, null=True, blank=True)
    log = models.JSONField(null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)


class BackupHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.BooleanField(default=True, null=True, blank=True)
    log = models.JSONField(null=True, blank=True, default='')
    service = models.ForeignKey(DBService, blank=True, null=True, on_delete=models.SET_NULL)
    folder = models.ForeignKey(FolderBackup, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=32, choices=(('backup', 'Backup'), ('folder', 'Folder')))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.id + " : " + self.type + "(" + str(
            self.created_at) + ")" + self.service +
                self.folder + " status :" + self.status)
