# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-29 16:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0031_auto_20190321_1836'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Journalist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TargetedJournalist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('incident', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='targeted_journalists', to='incident.IncidentPage')),
                ('institution', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='incident.Institution')),
                ('journalist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='incident.Journalist')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='incidentpage',
            name='targeted_institutions',
            field=models.ManyToManyField(blank=True, related_name='institutions_incidents', to='incident.Institution', verbose_name='Targeted Institutions'),
        ),
    ]
