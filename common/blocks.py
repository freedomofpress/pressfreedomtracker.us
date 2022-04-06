import re

from django.forms.utils import ErrorList

from wagtail.core import blocks
from wagtail.core.blocks.struct_block import StructBlockValidationError
from wagtail.core.rich_text import RichText
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from common.choices import BACKGROUND_COLOR_CHOICES
from common.templatetags.render_as_template import render_as_template
from common.utils import unescape
from common.validators import validate_template


class RichTextTemplateBlock(blocks.RichTextBlock):
    def __init__(self, features=None, **kwargs):
        if not features:
            features = [
                'h1',
                'h2',
                'h3',
                'h4',
                'h5',
                'h6',
                'bold',
                'italic',
                'ol',
                'ul',
                'hr',
                'link',
                'document-link',
                'image',
                'embed',
                'numincidents',  # Enhanced incident stats entry
            ]
        super().__init__(
            features=features,
            **kwargs,
        )

    def clean(self, value):
        cleaned_value = super(RichTextTemplateBlock, self).clean(value)
        # cleaned_value is a wagtail.core.rich_text.RichText instance.
        # RichText.source is the raw HTML value.
        validate_template(cleaned_value.source)
        return RichText(unescape(cleaned_value.source))

    def render_basic(self, value, context=None):
        return render_as_template(value)


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


class TweetEmbedBlock(blocks.StructBlock):
    tweet = EmbedBlock()

    class Meta:
        template = 'common/blocks/tweet_embed.html'
        icon = 'pick'
        label = 'Tweet'

    def clean(self, value):
        errors = {}
        twitter_url = r'^(http|https):\/\/twitter.com'
        tweet = value.get('tweet')

        if tweet:
            valid = re.match(twitter_url, tweet.url)

            if not valid:
                errors['tweet'] = ErrorList(['Please enter a valid Twitter URL.'])

            if errors:
                raise StructBlockValidationError(errors)

        return super().clean(value)


class AsideBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(
        features=[
            'bold',
            'italic',
            'h2',
            'h3',
            'h4',
            'ol',
            'ul',
            'hr',
            'embed',
            'link',
            'document-link',
            'image',
            'code',
        ],
    )

    class Meta:
        template = 'common/blocks/aside_block.html'
        icon = 'doc-full-inverse'
        label = 'Aside'


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

    text = blocks.RichTextBlock(
        features=[
            'bold',
            'italic',
            'h2',
            'h3',
            'h4',
            'ol',
            'ul',
            'hr',
            'embed',
            'link',
            'document-link',
            'image',
            'code',
        ],
    )

    # These fields are assumed to be deprecated and are left for legacy purposes
    # The template does not use the values of these fields
    background_color = blocks.ChoiceBlock(choices=BACKGROUND_COLOR_CHOICES, default='white')
    text_align = blocks.ChoiceBlock(choices=TEXT_ALIGN_CHOICES, default='left')
    font_size = blocks.ChoiceBlock(choices=FONT_SIZE_CHOICES, default='normal')
    font_family = blocks.ChoiceBlock(choices=FONT_FAMILY_CHOICES, default='sans-serif')

    class Meta:
        template = 'common/blocks/styled_text.html'
        icon = 'doc-full'
        label = 'Styled Text Block'


class StyledTextTemplateBlock(StyledTextBlock):
    text = RichTextTemplateBlock(
        features=[
            'bold',
            'italic',
            'h2',
            'h3',
            'h4',
            'ol',
            'ul',
            'hr',
            'embed',
            'link',
            'document-link',
            'image',
            'code',
            'numincidents',  # Enhanced incident stats entry
        ],
    )

    def get_context(self, *args, **kwargs):
        context = super(StyledTextTemplateBlock, self).get_context(*args, **kwargs)
        context['render_as_template'] = True
        return context


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


class StatTableBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super(StatTableBlock, self).__init__(
            blocks.StructBlock([
                ('header', blocks.TextBlock(required=True)),
                ('value', blocks.CharBlock(required=True, validators=[validate_template])),
            ]),
            template='common/blocks/stat_table_block.html',
            **kwargs
        )

    class Meta:
        icon = 'list-ul'


class TabbedBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super(TabbedBlock, self).__init__(
            blocks.StructBlock([
                ('header', blocks.TextBlock(required=True)),
                ('value', blocks.StreamBlock([
                    ('heading_2', Heading2()),
                    ('raw_html', blocks.RawHTMLBlock()),
                    ('rich_text', blocks.RichTextBlock()),
                    ('tweet', TweetEmbedBlock()),
                ])),
            ]),
            template='common/blocks/tabbed_block.html',
            **kwargs
        )

    class Meta:
        icon = 'list-ul'


class ButtonBlock(blocks.StructBlock):
    text = blocks.TextBlock(required=True)
    url = blocks.URLBlock(required=True)

    class Meta:
        template = 'common/blocks/button.html'


class RichTextBlockQuoteBlock(blocks.StructBlock):
    text = blocks.RichTextBlock()
    source_text = blocks.RichTextBlock(required=False)
    source_url = blocks.URLBlock(required=False, help_text="Source text will link to this url.")

    class Meta:
        template = 'common/blocks/blockquote.html'
        icon = "openquote"


class PullQuoteBlock(blocks.StructBlock):
    text = blocks.TextBlock()

    class Meta:
        template = 'common/blocks/pull_quote_block.html'
        icon = "openquote"


class EmailSignupBlock(blocks.StructBlock):
    text = blocks.CharBlock(
        label='Call to action text',
        help_text='Defaults to sitewide setting',
        required=False
    )
    success_text = blocks.CharBlock(
        label='Success text',
        help_text='To be displayed after a successful signup. Defaults to sitewide setting',
        required=False
    )

    class Meta:
        template = 'common/blocks/emails_signup.html'
        icon = 'form'
        label = 'Newsletter Signup'


class AbstractInfoTableCTABlock(blocks.StructBlock):
    cta_label = blocks.CharBlock(
        help_text='Label to be displayed for row link, e.g. "Read the bio", "Contact us", "Visit the page", etc.',
    )

    class Meta:
        abstract = True


class InfoTableBlockPage(AbstractInfoTableCTABlock):
    table_data = blocks.ListBlock(blocks.StructBlock(
        [
            ('page', blocks.PageChooserBlock()),
            ('title', blocks.CharBlock(
                help_text='Optional: defaults to page title',
                required=False,
            )),
            ('description', blocks.CharBlock()),
        ],
        icon='list-ul',
        label='Table row'
    ))

    class Meta:
        template = 'common/blocks/info_table/_page.html'
        icon = 'doc-full'


class InfoTableBlockEmail(AbstractInfoTableCTABlock):
    table_data = blocks.ListBlock(blocks.StructBlock(
        [
            ('title', blocks.CharBlock()),
            ('email', blocks.EmailBlock()),
        ],
        icon='list-ul',
        label='Table row'
    ))

    class Meta:
        template = 'common/blocks/info_table/_email.html'
        icon = 'mail'


class InfoTableBlockURL(AbstractInfoTableCTABlock):
    table_data = blocks.ListBlock(blocks.StructBlock(
        [
            ('image', ImageChooserBlock(
                required=False,
            )),
            ('title', blocks.CharBlock()),
            ('url', blocks.URLBlock()),
        ],
        icon='list-ul',
        label='Table row'
    ))

    class Meta:
        template = 'common/blocks/info_table/_url.html'
        icon = 'site'


class InfoTableBlockText(blocks.StructBlock):
    table_data = blocks.ListBlock(blocks.StructBlock(
        [
            ('title', blocks.CharBlock()),
            ('description', blocks.CharBlock()),
        ],
        icon='list-ul',
        label='Table row',
    ))

    class Meta:
        template = 'common/blocks/info_table/_text.html'
        icon = 'pilcrow'


class InfoTableBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        help_text='Heading of the info table',
    )
    table = blocks.StreamBlock(
        [
            ('page_links', InfoTableBlockPage()),
            ('email_addresses', InfoTableBlockEmail()),
            ('external_links', InfoTableBlockURL()),
            ('plain_text', InfoTableBlockText()),
        ],
        max_num=1,
        icon='list-ul',
        label='Table type'
    )

    class Meta:
        template = 'common/blocks/info_table.html'
        icon = 'list-ul'
        label = 'Info table'
