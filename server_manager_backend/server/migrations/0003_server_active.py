# Generated by Django 4.0.10 on 2024-07-06 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_alter_action_name_alter_dbservice_dbname_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]