# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-04 19:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20170704_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statbox',
            name='color',
            field=models.CharField(choices=[('blue', 'Blue'), ('green', 'Green'), ('purple', 'Purple'), ('orange', 'Orange'), ('dark-gray', 'Dark Gray'), ('white', 'White')], max_length=7),
        ),
    ]
