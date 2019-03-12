# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-24 00:01
from __future__ import unicode_literals

import common.blocks
from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0052_auto_20180320_0014'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incidentfiltersettings',
            options={'verbose_name': 'general incident filters'},
        ),
        migrations.AlterField(
            model_name='categoryincidentfilter',
            name='incident_filter',
            field=models.CharField(choices=[('actor', 'Actor'), ('affiliation', 'Affiliation'), ('arrest_status', 'Arrest status'), ('assailant', 'Assailant'), ('border_point', 'Border point'), ('charged_under_espionage_act', 'Charged under espionage act?'), ('charges', 'Charges'), ('circuits', 'Circuits'), ('city', 'City'), ('current_charges', 'Current Charges'), ('denial_of_entry', 'Denied entry?'), ('detention_date', 'Detention date between'), ('detention_status', 'Detention status'), ('did_authorities_ask_for_device_access', 'Did authorities ask for device access?'), ('did_authorities_ask_for_social_media_pass', 'Did authorities ask for social media password?'), ('did_authorities_ask_for_social_media_user', 'Did authorities ask for social media username?'), ('did_authorities_ask_about_work', "Did authorities ask intrusive questions about journalist's work?"), ('dropped_charges', 'Dropped Charges'), ('equipment_broken', 'Equipment Broken'), ('equipment_seized', 'Equipment Seized'), ('tags', 'Has any of these tags'), ('held_in_contempt', 'If subject refused to cooperate, were they held in contempt?'), ('links', 'Incident page links'), ('targets_whose_communications_were_obtained', 'Journalists/Organizations whose communications were obtained in leak investigation'), ('lawsuit_name', 'Lawsuit name'), ('legal_order_type', 'Legal order type'), ('politicians_or_public_figures_involved', 'Politicians or public officials involved'), ('release_date', 'Release date between'), ('is_search_warrant_obtained', 'Search warrant obtained?'), ('state', 'State'), ('status_of_charges', 'Status of charges'), ('status_of_prior_restraint', 'Status of prior restraint'), ('status_of_seized_equipment', 'Status of seized equipment'), ('stopped_at_border', 'Stopped at border?'), ('stopped_previously', 'Stopped previously?'), ('subpoena_status', 'Subpoena status'), ('subpoena_type', 'Subpoena type'), ('target_nationality', 'Target Nationality'), ('targets', 'Targeted any of these journalists'), ('third_party_business', 'Third party business'), ('third_party_in_possession_of_communications', 'Third party in possession of communications'), ('date', 'Took place between'), ('target_us_citizenship_status', 'US Citizenship Status'), ('unnecessary_use_of_force', 'Unnecessary use of force?'), ('venue', 'Venue'), ('was_journalist_targeted', 'Was journalist targeted?'), ('were_devices_searched_or_seized', 'Were devices searched or seized?')], max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='generalincidentfilter',
            name='incident_filter',
            field=models.CharField(choices=[('actor', 'Actor'), ('affiliation', 'Affiliation'), ('arrest_status', 'Arrest status'), ('assailant', 'Assailant'), ('border_point', 'Border point'), ('charged_under_espionage_act', 'Charged under espionage act?'), ('charges', 'Charges'), ('circuits', 'Circuits'), ('city', 'City'), ('current_charges', 'Current Charges'), ('denial_of_entry', 'Denied entry?'), ('detention_date', 'Detention date between'), ('detention_status', 'Detention status'), ('did_authorities_ask_for_device_access', 'Did authorities ask for device access?'), ('did_authorities_ask_for_social_media_pass', 'Did authorities ask for social media password?'), ('did_authorities_ask_for_social_media_user', 'Did authorities ask for social media username?'), ('did_authorities_ask_about_work', "Did authorities ask intrusive questions about journalist's work?"), ('dropped_charges', 'Dropped Charges'), ('equipment_broken', 'Equipment Broken'), ('equipment_seized', 'Equipment Seized'), ('tags', 'Has any of these tags'), ('held_in_contempt', 'If subject refused to cooperate, were they held in contempt?'), ('links', 'Incident page links'), ('targets_whose_communications_were_obtained', 'Journalists/Organizations whose communications were obtained in leak investigation'), ('lawsuit_name', 'Lawsuit name'), ('legal_order_type', 'Legal order type'), ('politicians_or_public_figures_involved', 'Politicians or public officials involved'), ('release_date', 'Release date between'), ('is_search_warrant_obtained', 'Search warrant obtained?'), ('state', 'State'), ('status_of_charges', 'Status of charges'), ('status_of_prior_restraint', 'Status of prior restraint'), ('status_of_seized_equipment', 'Status of seized equipment'), ('stopped_at_border', 'Stopped at border?'), ('stopped_previously', 'Stopped previously?'), ('subpoena_status', 'Subpoena status'), ('subpoena_type', 'Subpoena type'), ('target_nationality', 'Target Nationality'), ('targets', 'Targeted any of these journalists'), ('third_party_business', 'Third party business'), ('third_party_in_possession_of_communications', 'Third party in possession of communications'), ('date', 'Took place between'), ('target_us_citizenship_status', 'US Citizenship Status'), ('unnecessary_use_of_force', 'Unnecessary use of force?'), ('venue', 'Venue'), ('was_journalist_targeted', 'Was journalist targeted?'), ('were_devices_searched_or_seized', 'Were devices searched or seized?')], max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='simplepage',
            name='body',
            field=wagtail.core.fields.StreamField((('text', wagtail.core.blocks.StructBlock((('text', common.blocks.RichTextTemplateBlock()), ('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('white', 'White'), ('eastern-blue', 'Eastern Blue'), ('gamboge', 'Gamboge'), ('green', 'Green'), ('pink', 'Pink'), ('red', 'Red'), ('royal-blue', 'Royal Blue'), ('teal', 'Teal'), ('violet', 'Violet'), ('dark-gray', 'Dark Gray')])), ('text_align', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')])), ('font_size', wagtail.core.blocks.ChoiceBlock(choices=[('small', 'Small'), ('normal', 'Normal'), ('large', 'Large'), ('jumbo', 'Jumbo')])), ('font_family', wagtail.core.blocks.ChoiceBlock(choices=[('sans-serif', 'Sans Serif'), ('serif', 'Serif')]))), label='Text', template='common/blocks/styled_text_full_bleed.html')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock(help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.', required=False)), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('raw_html', wagtail.core.blocks.RawHTMLBlock()), ('blockquote', wagtail.core.blocks.StructBlock((('text', wagtail.core.blocks.RichTextBlock()), ('source_text', wagtail.core.blocks.RichTextBlock(required=False)), ('source_url', wagtail.core.blocks.URLBlock(help_text='Source text will link to this url.', required=False))))), ('list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('logo_list', common.blocks.LogoListBlock()), ('video', wagtail.core.blocks.StructBlock((('video', wagtail.embeds.blocks.EmbedBlock()), ('caption', wagtail.core.blocks.RichTextBlock(help_text='Video description displayed below the video.', required=False)), ('attribution', wagtail.core.blocks.CharBlock(help_text='Organization / Director.', max_length=255, required=False)), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('heading_1', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('heading_2', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('heading_3', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('email_signup', wagtail.core.blocks.StructBlock((('text', wagtail.core.blocks.CharBlock(help_text='Defaults to sitewide setting', label='Call to action text', required=False)), ('success_text', wagtail.core.blocks.CharBlock(help_text='To be displayed after a successful signup. Defaults to sitewide setting', label='Success text', required=False))))))),
        ),
        migrations.AlterField(
            model_name='simplepagewithsidebar',
            name='body',
            field=wagtail.core.fields.StreamField((('text', wagtail.core.blocks.StructBlock((('text', wagtail.core.blocks.RichTextBlock()), ('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('white', 'White'), ('eastern-blue', 'Eastern Blue'), ('gamboge', 'Gamboge'), ('green', 'Green'), ('pink', 'Pink'), ('red', 'Red'), ('royal-blue', 'Royal Blue'), ('teal', 'Teal'), ('violet', 'Violet'), ('dark-gray', 'Dark Gray')])), ('text_align', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')])), ('font_size', wagtail.core.blocks.ChoiceBlock(choices=[('small', 'Small'), ('normal', 'Normal'), ('large', 'Large'), ('jumbo', 'Jumbo')])), ('font_family', wagtail.core.blocks.ChoiceBlock(choices=[('sans-serif', 'Sans Serif'), ('serif', 'Serif')]))), label='Text')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock(help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.', required=False)), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('raw_html', wagtail.core.blocks.RawHTMLBlock()), ('blockquote', wagtail.core.blocks.StructBlock((('text', wagtail.core.blocks.RichTextBlock()), ('source_text', wagtail.core.blocks.RichTextBlock(required=False)), ('source_url', wagtail.core.blocks.URLBlock(help_text='Source text will link to this url.', required=False))))), ('list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('logo_list', common.blocks.LogoListBlock()), ('video', wagtail.core.blocks.StructBlock((('video', wagtail.embeds.blocks.EmbedBlock()), ('caption', wagtail.core.blocks.RichTextBlock(help_text='Video description displayed below the video.', required=False)), ('attribution', wagtail.core.blocks.CharBlock(help_text='Organization / Director.', max_length=255, required=False)), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('heading_1', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('heading_2', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('heading_3', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('email_signup', wagtail.core.blocks.StructBlock((('text', wagtail.core.blocks.CharBlock(help_text='Defaults to sitewide setting', label='Call to action text', required=False)), ('success_text', wagtail.core.blocks.CharBlock(help_text='To be displayed after a successful signup. Defaults to sitewide setting', label='Success text', required=False))))))),
        ),
    ]
