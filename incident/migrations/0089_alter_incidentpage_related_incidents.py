# Generated by Django 4.2.8 on 2023-12-26 14:21

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0088_auto_20240123_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidentpage',
            name='related_incidents',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='incident.incidentpage'),
        ),
    ]
