# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-29 16:27
from __future__ import unicode_literals

from django.db import migrations


def copy_targets(apps, schema_editor):
    """Copy Target data into separate tables based on kind

    This function copies all Target data on all Incidents into either
    the Journalist or Institution models and establishes appropriate
    relationships back to the original Incident.

    """

    IncidentPage = apps.get_model('incident', 'IncidentPage')
    Journalist = apps.get_model('incident', 'Journalist')
    TargetedJournalist = apps.get_model('incident', 'TargetedJournalist')
    Institution = apps.get_model('incident', 'Institution')

    for incident in IncidentPage.objects.all():
        for target in incident.targets.all():
            if target.kind == 'JOURNALIST':
                journalist, _ = Journalist.objects.get_or_create(title=target.title)
                TargetedJournalist.objects.create(
                    incident=incident,
                    journalist=journalist,
                    institution=None,
                )
            elif target.kind == 'INSTITUTION':
                inst, _ = Institution.objects.get_or_create(title=target.title)
                incident.targeted_institutions.add(inst)
                incident.save()


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0032_auto_20190429_1621'),
    ]

    operations = [
        migrations.RunPython(
            copy_targets,
            reverse_code=migrations.RunPython.noop,
            elidable=True,
        ),
    ]