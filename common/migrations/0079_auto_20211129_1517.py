# Generated by Django 2.2.24 on 2021-11-29 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0078_categorypage_default_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryincidentfilter',
            name='incident_filter',
            field=models.CharField(choices=[('actor', 'Actor'), ('arrest_status', 'Arrest status'), ('arresting_authority', 'Arresting authority'), ('assailant', 'Assailant'), ('border_point', 'Border point'), ('case_number', 'Case number'), ('charged_under_espionage_act', 'Charged under espionage act?'), ('charges', 'Charges'), ('circuits', 'Circuits'), ('city', 'City'), ('current_charges', 'Current Charges'), ('denial_of_entry', 'Denied entry?'), ('detention_date', 'Detention date between'), ('detention_status', 'Detention status'), ('did_authorities_ask_for_device_access', 'Did authorities ask for device access?'), ('did_authorities_ask_for_social_media_pass', 'Did authorities ask for social media password?'), ('did_authorities_ask_for_social_media_user', 'Did authorities ask for social media username?'), ('did_authorities_ask_about_work', "Did authorities ask intrusive questions about journalist's work?"), ('dropped_charges', 'Dropped Charges'), ('equipment_broken', 'Equipment Broken'), ('equipment_seized', 'Equipment Seized'), ('tags', 'Has any of these tags'), ('held_in_contempt', 'If subject refused to cooperate, were they held in contempt?'), ('authors', 'Incident author'), ('links', 'Incident page links'), ('lawsuit_name', 'Lawsuit name'), ('case_statuses', 'Legal case statuses'), ('legal_order_type', 'Legal order type'), ('politicians_or_public_figures_involved', 'Politicians or public officials involved'), ('primary_video', 'Primary video'), ('release_date', 'Release date between'), ('is_search_warrant_obtained', 'Search warrant obtained?'), ('pending_cases', 'Show only pending cases'), ('state', 'State'), ('status_of_charges', 'Status of charges'), ('status_of_prior_restraint', 'Status of prior restraint'), ('status_of_seized_equipment', 'Status of seized equipment'), ('stopped_at_border', 'Stopped at border?'), ('stopped_previously', 'Stopped previously?'), ('subpoena_statuses', 'Subpoena status'), ('subpoena_type', 'Subpoena type'), ('suppress_footer', 'Suppress Footer Call to Action'), ('target_nationality', 'Target Nationality'), ('targeted_institutions', 'Targeted Institutions'), ('targeted_journalists', 'Targeted any of these journalists'), ('workers_whose_communications_were_obtained', 'Targets whose communications were obtained in leak investigation'), ('third_party_business', 'Third party business'), ('third_party_in_possession_of_communications', 'Third party in possession of communications'), ('date', 'Took place between'), ('target_us_citizenship_status', 'US Citizenship Status'), ('unnecessary_use_of_force', 'Unnecessary use of force?'), ('recently_updated', 'Updated in the last'), ('venue', 'Venue'), ('was_journalist_targeted', 'Was journalist targeted?'), ('were_devices_searched_or_seized', 'Were devices searched or seized?')], max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='generalincidentfilter',
            name='incident_filter',
            field=models.CharField(choices=[('actor', 'Actor'), ('arrest_status', 'Arrest status'), ('arresting_authority', 'Arresting authority'), ('assailant', 'Assailant'), ('border_point', 'Border point'), ('case_number', 'Case number'), ('charged_under_espionage_act', 'Charged under espionage act?'), ('charges', 'Charges'), ('circuits', 'Circuits'), ('city', 'City'), ('current_charges', 'Current Charges'), ('denial_of_entry', 'Denied entry?'), ('detention_date', 'Detention date between'), ('detention_status', 'Detention status'), ('did_authorities_ask_for_device_access', 'Did authorities ask for device access?'), ('did_authorities_ask_for_social_media_pass', 'Did authorities ask for social media password?'), ('did_authorities_ask_for_social_media_user', 'Did authorities ask for social media username?'), ('did_authorities_ask_about_work', "Did authorities ask intrusive questions about journalist's work?"), ('dropped_charges', 'Dropped Charges'), ('equipment_broken', 'Equipment Broken'), ('equipment_seized', 'Equipment Seized'), ('tags', 'Has any of these tags'), ('held_in_contempt', 'If subject refused to cooperate, were they held in contempt?'), ('authors', 'Incident author'), ('links', 'Incident page links'), ('lawsuit_name', 'Lawsuit name'), ('case_statuses', 'Legal case statuses'), ('legal_order_type', 'Legal order type'), ('politicians_or_public_figures_involved', 'Politicians or public officials involved'), ('primary_video', 'Primary video'), ('release_date', 'Release date between'), ('is_search_warrant_obtained', 'Search warrant obtained?'), ('pending_cases', 'Show only pending cases'), ('state', 'State'), ('status_of_charges', 'Status of charges'), ('status_of_prior_restraint', 'Status of prior restraint'), ('status_of_seized_equipment', 'Status of seized equipment'), ('stopped_at_border', 'Stopped at border?'), ('stopped_previously', 'Stopped previously?'), ('subpoena_statuses', 'Subpoena status'), ('subpoena_type', 'Subpoena type'), ('suppress_footer', 'Suppress Footer Call to Action'), ('target_nationality', 'Target Nationality'), ('targeted_institutions', 'Targeted Institutions'), ('targeted_journalists', 'Targeted any of these journalists'), ('workers_whose_communications_were_obtained', 'Targets whose communications were obtained in leak investigation'), ('third_party_business', 'Third party business'), ('third_party_in_possession_of_communications', 'Third party in possession of communications'), ('date', 'Took place between'), ('target_us_citizenship_status', 'US Citizenship Status'), ('unnecessary_use_of_force', 'Unnecessary use of force?'), ('recently_updated', 'Updated in the last'), ('venue', 'Venue'), ('was_journalist_targeted', 'Was journalist targeted?'), ('were_devices_searched_or_seized', 'Were devices searched or seized?')], max_length=255, unique=True),
        ),
    ]
