# Generated by Django 3.2.22 on 2023-10-18 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0083_incident_metadata_updates_part_1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incidentpage',
            name='did_authorities_ask_for_social_media_pass',
        ),
        migrations.RemoveField(
            model_name='incidentpage',
            name='did_authorities_ask_for_social_media_user',
        ),
        migrations.RemoveField(
            model_name='incidentpage',
            name='stopped_at_border',
        ),
        migrations.RemoveField(
            model_name='incidentpage',
            name='were_devices_searched_or_seized',
        ),
    ]
