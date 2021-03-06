# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-23 02:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0039_auto_20180223_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryincidentfilter',
            name='category',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_filters', to='common.CategoryPage'),
        ),
        migrations.AlterField(
            model_name='categoryincidentfilter',
            name='incident_filter',
            field=models.CharField(choices=[('held_in_contempt', 'If subject refused to cooperate, were they held in contempt?'), ('charges', None), ('arrest_status', 'Arrest status'), ('links', 'incident page links'), ('current_charges', 'Current Charges'), ('did_authorities_ask_for_social_media_pass', 'Did authorities ask for social media password?'), ('is_search_warrant_obtained', 'Search warrant obtained?'), ('release_date', 'Release date'), ('legal_order_type', 'Legal order type'), ('subpoena_status', 'Subpoena status'), ('did_authorities_ask_for_social_media_user', 'Did authorities ask for social media username?'), ('targets_whose_communications_were_obtained', 'Journalists/Organizations whose communications were obtained in leak investigation'), ('did_authorities_ask_about_work', "Did authorities ask intrusive questions about journalist's work?"), ('dropped_charges', 'Dropped Charges'), ('stopped_previously', 'Stopped previously?'), ('third_party_in_possession_of_communications', 'Third party in possession of communications'), ('status_of_charges', 'Status of charges'), ('border_point', 'Border point'), ('charged_under_espionage_act', 'Charged under espionage act?'), ('were_devices_searched_or_seized', 'Were devices searched or seized?'), ('equipment_seized', 'Equipment Seized'), ('stopped_at_border', 'Stopped at border?'), ('did_authorities_ask_for_device_access', 'Did authorities ask for device access?'), ('actor', 'Actor'), ('status_of_seized_equipment', 'Status of seized equipment'), ('detention_status', 'Detention status'), ('target_nationality', 'Target Nationality'), ('equipment_broken', 'Equipment Broken'), ('politicians_or_public_figures_involved', 'Politicians or public officials involved'), ('target_us_citizenship_status', 'US Citizenship Status'), ('unnecessary_use_of_force', 'Unnecessary use of force?'), ('third_party_business', 'Third party business'), ('status_of_prior_restraint', 'Status of prior restraint'), ('subpoena_type', 'Subpoena type'), ('assailant', 'Assailant'), ('detention_date', 'Detention date'), ('denial_of_entry', 'Denied entry?'), ('was_journalist_targeted', 'Was journalist targeted?')], max_length=255),
        ),
    ]
