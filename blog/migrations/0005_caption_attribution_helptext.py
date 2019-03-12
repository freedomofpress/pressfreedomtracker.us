# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 18:16
from __future__ import unicode_literals

from django.db import migrations
import statistics.blocks
import statistics.registry
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_add_blocks_to_blog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='body',
            field=wagtail.core.fields.StreamField((('text', wagtail.core.blocks.StructBlock((('text', wagtail.core.blocks.RichTextBlock()), ('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('blue', 'Blue'), ('green', 'Green'), ('purple', 'Purple'), ('orange', 'Orange'), ('dark-gray', 'Dark Gray'), ('white', 'White')])), ('text_align', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')])), ('font_size', wagtail.core.blocks.ChoiceBlock(choices=[('small', 'Small'), ('normal', 'Normal'), ('large', 'Large'), ('jumbo', 'Jumbo')])), ('font_family', wagtail.core.blocks.ChoiceBlock(choices=[('sans-serif', 'Sans Serif'), ('serif', 'Serif')]))), label='Text', template='common/blocks/styled_text_full_bleed.html')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock(help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.', required=False)), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('raw_html', wagtail.core.blocks.RawHTMLBlock()), ('blockquote', wagtail.core.blocks.BlockQuoteBlock()), ('list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('video', wagtail.core.blocks.StructBlock((('video', wagtail.embeds.blocks.EmbedBlock()), ('caption', wagtail.core.blocks.RichTextBlock(help_text='Video description displayed below the video.', required=False)), ('attribution', wagtail.core.blocks.CharBlock(help_text='Organization / Director.', max_length=255, required=False)), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))))), ('heading_1', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('heading_2', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('heading_3', wagtail.core.blocks.StructBlock((('content', wagtail.core.blocks.CharBlock()),))), ('statistics', wagtail.core.blocks.StructBlock((('visualization', wagtail.core.blocks.ChoiceBlock(choices=statistics.blocks.get_visualization_choices)), ('dataset', wagtail.core.blocks.ChoiceBlock(choices=statistics.registry.get_stats_choices)), ('params', wagtail.core.blocks.CharBlock(help_text='Whitespace-separated list of arguments to be passed to the statistics function', required=False))))))),
        ),
        migrations.AlterField(
            model_name='blogpage',
            name='image_caption',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.', max_length=255, null=True),
        ),
    ]
