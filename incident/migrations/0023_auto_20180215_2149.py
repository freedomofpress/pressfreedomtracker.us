# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-15 21:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0022_add_verbose_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidentpage',
            name='denial_of_entry',
            field=models.BooleanField(default=False, verbose_name='Denied entry?'),
        ),
        migrations.AlterField(
            model_name='incidentpage',
            name='stopped_previously',
            field=models.BooleanField(default=False, verbose_name='Stopped previously?'),
        ),
    ]
