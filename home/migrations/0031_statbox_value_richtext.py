# Generated by Django 2.2.22 on 2021-05-10 17:12

import common.validators
from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0030_homepage_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statbox',
            name='value',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='Primary text for this stat box.  Line breaks will be removed.', null=True, validators=[common.validators.TemplateValidator()]),
        ),
    ]