# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-23 19:20
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0003_datetime_to_datefield'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentpage',
            name='image_attribution',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='incidentpage',
            name='image_caption',
            field=wagtail.core.fields.RichTextField(blank=True, max_length=255, null=True),
        ),
    ]
