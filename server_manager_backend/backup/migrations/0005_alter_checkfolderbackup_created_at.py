# Generated by Django 4.0.10 on 2024-06-24 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0004_alter_checkfolderbackup_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkfolderbackup',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]