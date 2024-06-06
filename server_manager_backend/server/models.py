import uuid

from django.db import models


class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    name = models.CharField()
    host = models.CharField()
    port = models.IntegerField()
    username = models.CharField()
    password = models.CharField()
    actions = models.ManyToManyField(to='Action', blank=True, on_delete=models.SET_NULL, )

    def __str__(self):
        return self.name + " - " + self.host + " - " + self.username


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL)
    name = models.CharField()
    command = models.TextField()

    def __str__(self):
        return self.id + ' - ' + self.server.name + ' - ' + self.command


class DBService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL)
    name = models.CharField()
    host = models.CharField()
    port = models.IntegerField()
    username = models.CharField()
    password = models.CharField()
    backup = models.BooleanField()

    def __str__(self):
        return self.id + " - " + self.name + " - " + self.host + " - " + self.username + " - " + self.backup


class Action(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True)
    server = models.ManyToManyField(to=Server, on_delete=models.SET_NULL, blank=True)
    command = models.TextField()
    onSuccess = models.TextField()
    onError = models.TextField()
    interval = models.IntegerField()

    def __str__(self):
        return self.id + '-' + self.command + ' - ' + self.onSuccess + ' - ' + self.onError
