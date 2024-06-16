import uuid

from django.db import models


class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    name = models.CharField(max_length=32)
    host = models.CharField(max_length=32)
    port = models.IntegerField()
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    actions = models.ManyToManyField(to='Action', blank=True, )

    def __str__(self):
        return self.name + " - " + self.host + " - " + self.username


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=32)
    command = models.TextField()
    contain = models.TextField()

    def __str__(self):
        return self.id + ' - ' + self.server.name + ' - ' + self.command


class DBService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True)
    dbName = models.CharField(max_length=32)
    serviceName = models.CharField(max_length=32,default='')
    host = models.CharField(max_length=32)
    port = models.IntegerField()
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    backup = models.BooleanField()

    def __str__(self):
        return self.id + " - " + self.dbName + " - " + self.host + " - " + self.username + " - " + self.backup


class Action(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    name = models.CharField(max_length=32)
    command = models.TextField()
    onSuccess = models.TextField()
    onError = models.TextField()
    interval = models.PositiveBigIntegerField()

    def __str__(self):
        return self.id + '-' + self.command + ' - ' + self.onSuccess + ' - ' + self.onError
