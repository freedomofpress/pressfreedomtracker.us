from wagtail.wagtailcore import blocks
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock

from common.choices import BACKGROUND_COLOR_CHOICES
from common.validators import validate_template


class RichTextTemplateBlock(blocks.RichTextBlock):
    def clean(self, value):
        cleaned_value = super(RichTextTemplateBlock, self).clean(value)
        validate_template(cleaned_value.source)
        return cleaned_value


class Heading1(blocks.StructBlock):
    content = blocks.CharBlock()

    class Meta:
        template = 'common/blocks/heading_1.html'
        icon = 'title'
        label = 'Heading 1'


class Heading2(blocks.StructBlock):
    content = blocks.CharBlock()

    class Meta:
        template = 'common/blocks/heading_2.html'
        icon = 'title'
        label = 'Heading 2'


class Heading3(blocks.StructBlock):
    content = blocks.CharBlock()

    class Meta:
        template = 'common/blocks/heading_3.html'
        icon = 'title'
        label = 'Heading 3'


ALIGNMENT_CHOICES = (
    ('left', 'Left'),
    ('right', 'Right'),
    ('full-width', 'Full Width'),
)


class AlignedCaptionedImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.RichTextBlock(
        required=False,
        help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.'
    )
    alignment = blocks.ChoiceBlock(choices=ALIGNMENT_CHOICES)

    class Meta:
        template = 'common/blocks/aligned_captioned_image.html'
        icon = 'image'
        label = 'Image'


class AlignedCaptionedEmbedBlock(blocks.StructBlock):
    video = EmbedBlock()
    caption = blocks.RichTextBlock(
        required=False,
        help_text='Video description displayed below the video.'
    )
    attribution = blocks.CharBlock(
        max_length=255,
        required=False,
        help_text='Organization / Director.'
    )
    alignment = blocks.ChoiceBlock(choices=ALIGNMENT_CHOICES)

    class Meta:
        template = 'common/blocks/aligned_captioned_embed.html'
        icon = 'media'
        label = 'Video'


class StyledTextBlock(blocks.StructBlock):
    TEXT_ALIGN_CHOICES = (
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    )

    FONT_SIZE_CHOICES = (
        ('small', 'Small'),
        ('normal', 'Normal'),
        ('large', 'Large'),
        ('jumbo', 'Jumbo'),
    )

    FONT_FAMILY_CHOICES = (
        ('sans-serif', 'Sans Serif'),
        ('serif', 'Serif'),
    )

    text = blocks.RichTextBlock()
    background_color = blocks.ChoiceBlock(choices=BACKGROUND_COLOR_CHOICES, default='white')
    text_align = blocks.ChoiceBlock(choices=TEXT_ALIGN_CHOICES, default='left')
    font_size = blocks.ChoiceBlock(choices=FONT_SIZE_CHOICES, default='normal')
    font_family = blocks.ChoiceBlock(choices=FONT_FAMILY_CHOICES, default='sans-serif')

    class Meta:
        template = 'common/blocks/styled_text.html'
        icon = 'doc-full'
        label = 'Styled Text Block'


class StyledTextTemplateBlock(StyledTextBlock):
    text = RichTextTemplateBlock()


class LogoListBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super(LogoListBlock, self).__init__(
            blocks.StructBlock([
                ('logo', ImageChooserBlock(required=True)),
                ('url', blocks.URLBlock(required=False)),
            ]),
            template='common/blocks/logo_list_block.html',
            **kwargs
        )

    class Meta:
        icon = 'list-ul'


class RichTextBlockQuoteBlock(blocks.StructBlock):
    text = blocks.RichTextBlock()
    source_text = blocks.RichTextBlock(required=False)
    source_url = blocks.URLBlock(required=False, help_text="Source text will link to this url.")

    class Meta:
        template = 'common/blocks/blockquote.html'
        icon = "openquote"
