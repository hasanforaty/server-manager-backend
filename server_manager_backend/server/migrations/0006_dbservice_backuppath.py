# Generated by Django 4.0.10 on 2024-06-23 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_rename_name_service_servicename'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbservice',
            name='backupPath',
            field=models.TextField(default='SM/backup'),
        ),
    ]
