# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-19 18:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0040_page_draft_title'),
        ('common', '0048_auto_20180314_1810'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralIncidentFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('incident_filter', models.CharField(choices=[('detention_status', 'Detention status'), ('status_of_seized_equipment', 'Status of seized equipment'), ('were_devices_searched_or_seized', 'Were devices searched or seized?'), ('third_party_business', 'Third party business'), ('status_of_charges', 'Status of charges'), ('target_us_citizenship_status', 'US Citizenship Status'), ('detention_date', 'Detention date'), ('dropped_charges', 'Dropped Charges'), ('assailant', 'Assailant'), ('status_of_prior_restraint', 'Status of prior restraint'), ('denial_of_entry', 'Denied entry?'), ('equipment_seized', 'Equipment Seized'), ('unnecessary_use_of_force', 'Unnecessary use of force?'), ('subpoena_status', 'Subpoena status'), ('is_search_warrant_obtained', 'Search warrant obtained?'), ('stopped_previously', 'Stopped previously?'), ('equipment_broken', 'Equipment Broken'), ('did_authorities_ask_about_work', "Did authorities ask intrusive questions about journalist's work?"), ('release_date', 'Release date'), ('did_authorities_ask_for_social_media_pass', 'Did authorities ask for social media password?'), ('did_authorities_ask_for_social_media_user', 'Did authorities ask for social media username?'), ('subpoena_type', 'Subpoena type'), ('held_in_contempt', 'If subject refused to cooperate, were they held in contempt?'), ('charged_under_espionage_act', 'Charged under espionage act?'), ('was_journalist_targeted', 'Was journalist targeted?'), ('third_party_in_possession_of_communications', 'Third party in possession of communications'), ('did_authorities_ask_for_device_access', 'Did authorities ask for device access?'), ('arrest_status', 'Arrest status'), ('politicians_or_public_figures_involved', 'Politicians or public officials involved'), ('current_charges', 'Current Charges'), ('charges', None), ('targets_whose_communications_were_obtained', 'Journalists/Organizations whose communications were obtained in leak investigation'), ('target_nationality', 'Target Nationality'), ('links', 'incident page links'), ('border_point', 'Border point'), ('legal_order_type', 'Legal order type'), ('actor', 'Actor'), ('stopped_at_border', 'Stopped at border?')], max_length=255)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IncidentFilterSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.Site')),
            ],
            options={
                'verbose_name': 'Incident Filters',
            },
        ),
        migrations.AddField(
            model_name='generalincidentfilter',
            name='incident_filter_settings',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='general_incident_filters', to='common.IncidentFilterSettings'),
        ),
    ]
