# Generated by Django 2.1.11 on 2019-10-10 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0038_auto_20191010_0923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incidentpage',
            name='subpoena_status',
        ),
    ]
