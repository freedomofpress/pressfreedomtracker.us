# Generated by Django 3.2.18 on 2023-04-25 23:06

import common.models.helpers
from django.db import migrations
import statistics.registry
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0030_add_vertical_bar_chart_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='body',
            field=wagtail.fields.StreamField([('text', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'h2', 'h3', 'h4', 'ol', 'ul', 'hr', 'embed', 'link', 'document-link', 'image', 'code'])), ('background_color', wagtail.blocks.ChoiceBlock(choices=[('white', 'White'), ('eastern-blue', 'Eastern Blue'), ('gamboge', 'Gamboge'), ('green', 'Green'), ('pink', 'Pink'), ('red', 'Red'), ('royal-blue', 'Royal Blue'), ('teal', 'Teal'), ('violet', 'Violet'), ('dark-gray', 'Dark Gray')])), ('text_align', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')])), ('font_size', wagtail.blocks.ChoiceBlock(choices=[('small', 'Small'), ('normal', 'Normal'), ('large', 'Large'), ('jumbo', 'Jumbo')])), ('font_family', wagtail.blocks.ChoiceBlock(choices=[('sans-serif', 'Sans Serif'), ('serif', 'Serif')]))], label='Text', template='common/blocks/styled_text_full_bleed.html')), ('aside', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'h2', 'h3', 'h4', 'ol', 'ul', 'hr', 'embed', 'link', 'document-link', 'image', 'code']))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.', required=False)), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))])), ('raw_html', wagtail.blocks.RawHTMLBlock()), ('tweet', wagtail.blocks.StructBlock([('tweet', wagtail.embeds.blocks.EmbedBlock())])), ('blockquote', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock()), ('source_text', wagtail.blocks.RichTextBlock(required=False)), ('source_url', wagtail.blocks.URLBlock(help_text='Source text will link to this url.', required=False))])), ('list', wagtail.blocks.ListBlock(wagtail.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('video', wagtail.blocks.StructBlock([('video', wagtail.embeds.blocks.EmbedBlock()), ('caption', wagtail.blocks.RichTextBlock(help_text='Video description displayed below the video.', required=False)), ('attribution', wagtail.blocks.CharBlock(help_text='Organization / Director.', max_length=255, required=False)), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('full-width', 'Full Width')]))])), ('heading_1', wagtail.blocks.StructBlock([('content', wagtail.blocks.CharBlock())])), ('heading_2', wagtail.blocks.StructBlock([('content', wagtail.blocks.CharBlock())])), ('heading_3', wagtail.blocks.StructBlock([('content', wagtail.blocks.CharBlock())])), ('button', wagtail.blocks.StructBlock([('text', wagtail.blocks.TextBlock(required=True)), ('url', wagtail.blocks.URLBlock(required=True))])), ('statistics', wagtail.blocks.StructBlock([('visualization', wagtail.blocks.ChoiceBlock(choices=statistics.registry.get_visualization_choices)), ('dataset', wagtail.blocks.ChoiceBlock(choices=statistics.registry.get_stats_choices)), ('params', wagtail.blocks.CharBlock(help_text='Whitespace-separated list of arguments to be passed to the statistics function', required=False))])), ('vertical_bar_chart', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('incident_set', wagtail.blocks.StructBlock([('category', wagtail.blocks.PageChooserBlock(help_text='If selected, only incidents in the chosen category will be included.', label='Filter by Category', page_type=['common.CategoryPage'], required=False)), ('tag', wagtail.blocks.ChoiceBlock(choices=common.models.helpers.get_tags, help_text='If selected, only incidents with the chosen tag will be included.', label='Filter by Tag', required=False)), ('lower_date', wagtail.blocks.DateBlock(help_text='If set, no incidents before this date will be included.', label='Filter by Date, lower bound', required=False)), ('upper_date', wagtail.blocks.DateBlock(help_text='If set, no incidents after this date will be included.', label='Filter by Date, upper bound', required=False))])), ('description', wagtail.blocks.TextBlock(help_text='Description for assistive technology users. If the chart is demonstrating a specific trend, try to include that, e.g., "Bar chart showing a decreasing number of assaults over the course of 2023."', required=True))])), ('tree_map_chart', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('incident_set', wagtail.blocks.StructBlock([('category', wagtail.blocks.PageChooserBlock(help_text='If selected, only incidents in the chosen category will be included.', label='Filter by Category', page_type=['common.CategoryPage'], required=False)), ('tag', wagtail.blocks.ChoiceBlock(choices=common.models.helpers.get_tags, help_text='If selected, only incidents with the chosen tag will be included.', label='Filter by Tag', required=False)), ('lower_date', wagtail.blocks.DateBlock(help_text='If set, no incidents before this date will be included.', label='Filter by Date, lower bound', required=False)), ('upper_date', wagtail.blocks.DateBlock(help_text='If set, no incidents after this date will be included.', label='Filter by Date, upper bound', required=False))])), ('description', wagtail.blocks.TextBlock(help_text='Description for assistive technology users. If the chart is demonstrating a specific trend, try to include that, e.g., "Bar chart showing a decreasing number of assaults over the course of 2023."', required=True))]))], use_json_field=True),
        ),
    ]