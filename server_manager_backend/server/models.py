import uuid

from django.db import models


class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    actions = models.ManyToManyField('Action', blank=True, related_name='servers')
    active = models.BooleanField(default=True)
    log = models.TextField(default='')

    def __str__(self):
        return self.name + " - " + self.host + " - " + self.username


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True)
    serviceName = models.CharField(max_length=255)
    command = models.TextField()
    contain = models.TextField()

    def __str__(self):
        return self.id + ' - ' + self.server.name + ' - ' + self.command


class DBService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True)
    dbName = models.CharField(max_length=255)
    serviceName = models.CharField(max_length=255, default='')
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    backup = models.BooleanField()
    backupPath = models.TextField(default='SM/backup')
    type = models.CharField(choices=[('mysql', 'MySql'), ('postgres', 'Postgres')], default='postgres',max_length=255)

    def __str__(self):
        return self.id + " - " + self.dbName + " - " + self.host + " - " + self.username + " - " + self.backup


class Action(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    name = models.CharField(max_length=255)
    command = models.TextField()
    description = models.TextField(default='')
    interval = models.PositiveBigIntegerField()

    def __str__(self):
        return str(self.id) + '-' + self.command + ' - ' + self.description + ' - ' + self.name
