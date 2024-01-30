# Generated by Django 3.2.22 on 2023-11-07 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0085_add_type_of_denial'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentpage',
            name='mistakenly_released_materials',
            field=models.BooleanField(default=False, verbose_name='Mistakenly released materials?'),
        ),
    ]