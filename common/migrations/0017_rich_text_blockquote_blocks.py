# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-19 18:43
from __future__ import unicode_literals

import common.blocks
from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0016_caption_attribution_helptext'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simplepage',
            name='body',
            field=wagtail.fields.StreamField((('text', wagtail.blocks.StructBlock((('text', wagtail.blocks.RichTextBlock()), ('background_color', wagtail.blocks.ChoiceBlock(choices=[('blue', 'Blue'), ('green', 'Green'), ('purple', 'Purple'), ('orange', 'Orange'), ('dark-gray', 'Dark Gray'), ('white', 'White')])), ('text_align', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')])), ('font_size', wagtail.blocks.ChoiceBlock(choices=[('small', 'Small'), ('normal', 'Normal'), ('large', 'Large'), ('jumbo', 'Jumbo')])), ('font_family', wagtail.blocks.ChoiceBlock(choices=[('sans-serif', 'Sans Serif'), ('serif', 'Serif')]))), label='Text', template='common/blocks/styled_text_full_bleed.html')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.', required=False)), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('raw_html', wagtail.blocks.RawHTMLBlock()), ('blockquote', common.blocks.RichTextBlockQuoteBlock()), ('list', wagtail.blocks.ListBlock(wagtail.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('logo_list', common.blocks.LogoListBlock()), ('video', wagtail.blocks.StructBlock((('video', wagtail.embeds.blocks.EmbedBlock()), ('caption', wagtail.blocks.RichTextBlock(help_text='Video description displayed below the video.', required=False)), ('attribution', wagtail.blocks.CharBlock(help_text='Organization / Director.', max_length=255, required=False)), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('heading_1', wagtail.blocks.StructBlock((('content', wagtail.blocks.CharBlock()),))), ('heading_2', wagtail.blocks.StructBlock((('content', wagtail.blocks.CharBlock()),))), ('heading_3', wagtail.blocks.StructBlock((('content', wagtail.blocks.CharBlock()),))))),
        ),
        migrations.AlterField(
            model_name='simplepagewithsidebar',
            name='body',
            field=wagtail.fields.StreamField((('text', wagtail.blocks.StructBlock((('text', wagtail.blocks.RichTextBlock()), ('background_color', wagtail.blocks.ChoiceBlock(choices=[('blue', 'Blue'), ('green', 'Green'), ('purple', 'Purple'), ('orange', 'Orange'), ('dark-gray', 'Dark Gray'), ('white', 'White')])), ('text_align', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')])), ('font_size', wagtail.blocks.ChoiceBlock(choices=[('small', 'Small'), ('normal', 'Normal'), ('large', 'Large'), ('jumbo', 'Jumbo')])), ('font_family', wagtail.blocks.ChoiceBlock(choices=[('sans-serif', 'Sans Serif'), ('serif', 'Serif')]))), label='Text')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.', required=False)), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('raw_html', wagtail.blocks.RawHTMLBlock()), ('blockquote', common.blocks.RichTextBlockQuoteBlock()), ('list', wagtail.blocks.ListBlock(wagtail.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('logo_list', common.blocks.LogoListBlock()), ('video', wagtail.blocks.StructBlock((('video', wagtail.embeds.blocks.EmbedBlock()), ('caption', wagtail.blocks.RichTextBlock(help_text='Video description displayed below the video.', required=False)), ('attribution', wagtail.blocks.CharBlock(help_text='Organization / Director.', max_length=255, required=False)), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('heading_1', wagtail.blocks.StructBlock((('content', wagtail.blocks.CharBlock()),))), ('heading_2', wagtail.blocks.StructBlock((('content', wagtail.blocks.CharBlock()),))), ('heading_3', wagtail.blocks.StructBlock((('content', wagtail.blocks.CharBlock()),))))),
        ),
    ]
