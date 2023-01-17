# Generated by Django 3.2.16 on 2023-01-18 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0094_update_streamfields_to_use_json_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statisticsitem',
            name='dataset',
            field=models.CharField(choices=[('num_incidents', 'num_incidents'), ('num_institution_targets', 'num_institution_targets'), ('num_journalist_targets', 'num_journalist_targets'), ('num_targets', 'num_targets')], default='num_incidents', max_length=255),
        ),
    ]
