# Generated by Django 2.2.9 on 2020-02-12 15:15

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0040_merge_20200127_1819'),
    ]

    operations = [
        migrations.CreateModel(
            name='GovernmentWorker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Government employee or contractor',
                'verbose_name_plural': 'Government employees or contractors',
            },
        ),
        migrations.AddField(
            model_name='incidentpage',
            name='workers_whose_communications_were_obtained',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, related_name='incidents', to='incident.GovernmentWorker', verbose_name='Targets whose communications were obtained in leak investigation'),
        ),
    ]
