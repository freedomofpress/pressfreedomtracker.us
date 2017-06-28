# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-28 22:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0005_merge_20170626_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidentpage',
            name='teaser_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='common.CustomImage'),
        ),
    ]
