# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-10 16:09
from __future__ import unicode_literals

from django.db import migrations
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('incident', '0019_auto_20170510_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentpage',
            name='targets',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='incident.TargetsTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
