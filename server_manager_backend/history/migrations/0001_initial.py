# Generated by Django 4.0.10 on 2024-06-11 05:51

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('server', '0001_initial'),
        ('backup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceHistory',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('server', 'Server'), ('service', 'Service')], max_length=32)),
                ('status', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='server.service')),
                ('serviceDB', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='server.dbservice')),
            ],
        ),
        migrations.CreateModel(
            name='ServerInfo',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cpu', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)])),
                ('ram', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)])),
                ('memory', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('server', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='server.server')),
            ],
        ),
        migrations.CreateModel(
            name='BackupHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('backup', 'Backup'), ('folder', 'Folder')], max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='backup.folderbackup')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='server.dbservice')),
            ],
        ),
        migrations.CreateModel(
            name='ActionHistory',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('log', models.JSONField(blank=True, default=dict, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=False)),
                ('action', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='server.action')),
                ('server', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='server.server')),
            ],
        ),
    ]
