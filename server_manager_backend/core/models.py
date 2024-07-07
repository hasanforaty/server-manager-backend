from django.db import models


class CacheModel(models.Model):
    json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class TaskModel(models.Model):
    active = models.BooleanField(default=True)
