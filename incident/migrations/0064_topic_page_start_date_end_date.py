# Generated by Django 2.2.24 on 2021-07-06 14:40

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0063_incidentindexpage_feed_per_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicpage',
            name='end_date',
            field=models.DateField(blank=True, help_text='End date for this topic. No incidents after this date will be included.', null=True),
        ),
        migrations.AddField(
            model_name='topicpage',
            name='start_date',
            field=models.DateField(blank=True, help_text='Start date for this topic. No incidents before this date will be included.', null=True),
        ),
        migrations.AddConstraint(
            model_name='topicpage',
            constraint=models.CheckConstraint(check=models.Q(start_date__lte=django.db.models.expressions.F('end_date')), name='start_date_end_date_order'),
        ),
    ]
