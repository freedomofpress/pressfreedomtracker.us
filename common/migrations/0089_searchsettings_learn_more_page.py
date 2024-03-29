# Generated by Django 3.2.12 on 2022-03-21 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('common', '0088_auto_20220315_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchsettings',
            name='learn_more_page',
            field=models.ForeignKey(blank=True, help_text='Page linked to by the "Learn More" link in the Download Dataset dropdown on the incident database page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.page'),
        ),
    ]
