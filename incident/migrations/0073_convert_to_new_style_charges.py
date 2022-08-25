# Generated by Django 3.2.15 on 2022-08-18 15:41
from django.db import migrations
import itertools


def convert_charges(apps, schema_editor):
    IncidentPage = apps.get_model('incident', 'IncidentPage')
    IncidentCharge = apps.get_model('incident', 'IncidentCharge')
    for page in IncidentPage.objects.prefetch_related('current_charges', 'dropped_charges'):
        all_charges = itertools.chain(page.dropped_charges.all(), page.current_charges.all())
        for charge in all_charges:
            IncidentCharge.objects.get_or_create(
                incident_page=page,
                charge=charge,
                date=page.date,
                status='CHARGES_PENDING',
            )


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0072_create_incident_charges_and_updates'),
    ]

    operations = [
        migrations.RunPython(convert_charges),
    ]
