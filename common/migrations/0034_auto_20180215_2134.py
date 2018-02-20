# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-15 21:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0033_merge_20180215_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidentfieldcategorypage',
            name='incident_field',
            field=models.CharField(choices=[('categories', 'categories'), ('links', 'links'), ('equipment_seized', 'equipment_seized'), ('equipment_broken', 'equipment_broken'), ('page_ptr', 'page ptr'), ('search_image', 'search image'), ('date', 'date'), ('arrest_status', 'Arrest status'), ('status_of_charges', 'Status of charges'), ('release_date', 'Release date'), ('detention_date', 'Detention date'), ('unnecessary_use_of_force', 'Unnecessary use of force?'), ('status_of_seized_equipment', 'Status of seized equipment'), ('is_search_warrant_obtained', 'Search warrant obtained?'), ('actor', 'Actor'), ('border_point', 'Border point'), ('stopped_at_border', 'Stopped at border?'), ('target_us_citizenship_status', 'US Citizenship Status'), ('denial_of_entry', 'denial of entry'), ('stopped_previously', 'stopped previously'), ('did_authorities_ask_for_device_access', 'Did authorities ask for device access?'), ('did_authorities_ask_for_social_media_user', 'Did authorities ask for social media username?'), ('did_authorities_ask_for_social_media_pass', 'Did authorities ask for social media password?'), ('did_authorities_ask_about_work', "Did authorities ask intrusive questions about journalist's work?"), ('were_devices_searched_or_seized', 'Were devices searched or seized?'), ('assailant', 'Assailant'), ('was_journalist_targeted', 'Was journalist targeted?'), ('charged_under_espionage_act', 'Charged under espionage act?'), ('subpoena_type', 'Subpoena type'), ('subpoena_status', 'Subpoena status'), ('held_in_contempt', 'If subject refused to cooperate, were they held in contempt?'), ('detention_status', 'Detention status'), ('third_party_in_possession_of_communications', 'Third party in possession of communications'), ('third_party_business', 'Third party business'), ('legal_order_type', 'Legal order type'), ('status_of_prior_restraint', 'Status of prior restraint'), ('current_charges', 'Current Charges'), ('dropped_charges', 'Dropped Charges'), ('target_nationality', 'Target Nationality'), ('targets_whose_communications_were_obtained', 'Journalists/Organizations whose communications were obtained in leak investigation'), ('politicians_or_public_figures_involved', 'Politicians or public officials involved')], max_length=255),
        ),
    ]
