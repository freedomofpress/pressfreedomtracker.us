# Generated by Django 2.2.25 on 2021-12-08 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0066_auto_20211129_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentpage',
            name='case_type',
            field=models.CharField(blank=True, choices=[('CIVIL', 'Civil'), ('CLASS_ACTION', 'Class Action')], max_length=255, null=True, verbose_name='Type of case'),
        ),
    ]
