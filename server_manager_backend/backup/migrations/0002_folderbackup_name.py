# Generated by Django 4.0.10 on 2024-06-16 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='folderbackup',
            name='name',
            field=models.TextField(default=''),
        ),
    ]