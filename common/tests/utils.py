from random import choice
import json

from faker import Faker
from faker.providers import BaseProvider
from common.models import CustomImage
from common.choices import BACKGROUND_COLOR_CHOICES

from common.blocks import StyledTextBlock, ALIGNMENT_CHOICES

fake = Faker()


def generate_field(field_type, value):
    return {'type': field_type, 'value': value, 'id': fake.uuid4()}


def generate_styled_text(as_type='text'):
    background = choice([c[0] for c in BACKGROUND_COLOR_CHOICES])
    text_align = choice([c[0] for c in StyledTextBlock.TEXT_ALIGN_CHOICES])
    font_size = choice([c[0] for c in StyledTextBlock.FONT_SIZE_CHOICES])
    font_family = choice([c[0] for c in StyledTextBlock.FONT_FAMILY_CHOICES])
    text = fake.text()
    return generate_field(
        as_type,
        {
            'text': text,
            'background_color': background,
            'text_align': text_align,
            'font_size': font_size,
            'font_family': font_family,
        },
    )


def generate_styled_text_paragraphs(as_type='text'):
    background = 'white'
    text_align = 'left'
    font_size = 'normal'
    font_family = choice([c[0] for c in StyledTextBlock.FONT_FAMILY_CHOICES])
    paragraphs = (
        '<h3>{}</h3>'.format(fake.sentence()),
        '<p>{} <b>This sentence is in bold text.</b> {} '.format(
            fake.text(max_nb_chars=200), fake.text(max_nb_chars=200)
        ),
        '<a href="{}">This is a link to a fake url!</a> '.format(
            fake.url(schemes=['https'])
        ),
        '{}</p>'.format(fake.paragraph(nb_sentences=20, variable_nb_sentences=True)),
        '<p>{}</p>'.format(fake.paragraph(nb_sentences=20, variable_nb_sentences=True)),
        '<ul>',
        ''.join(['<li>{}</li>'.format(fake.word()) for i in range(10)]),
        '</ul><br />',
        '<p><a href="{}">This is a link to a fake url!</a></p>'.format(
            fake.url(schemes=['https'])
        ),
    )
    text = ''.join(paragraphs)
    return generate_field(
        as_type,
        {
            'text': text,
            'background_color': background,
            'text_align': text_align,
            'font_size': font_size,
            'font_family': font_family,
        },
    )


def generate_bare_image():
    image = choice(CustomImage.objects.filter(collection__name='Squares')).pk
    return generate_field('image', image)


def generate_rich_text_paragraph():
    paragraph = '<p>{}</p>'.format(fake.text(max_nb_chars=200))
    return generate_field('rich_text', paragraph)


def generate_rich_text():
    paragraphs = (
        '<h3>{}</h3>'.format(fake.sentence()),
        '<p>{} <b>This sentence is in bold text.</b> {} '.format(
            fake.text(max_nb_chars=200), fake.text(max_nb_chars=200)
        ),
        '<a href="{}">This is a link to a fake url!</a> '.format(
            fake.url(schemes=['https'])
        ),
        '{}</p>'.format(fake.paragraph(nb_sentences=20, variable_nb_sentences=True)),
        '<p>{}</p>'.format(fake.paragraph(nb_sentences=20, variable_nb_sentences=True)),
        '<ul>',
        ''.join(['<li>{}</li>'.format(fake.word()) for i in range(10)]),
        '</ul><br />',
        '<p><a href="{}">This is a link to a fake url!</a></p>'.format(
            fake.url(schemes=['https'])
        ),
    )
    return generate_field('rich_text', ''.join(paragraphs))


def generate_heading1_field():
    content = ' '.join(fake.words())

    return generate_field('heading_1', {'content': content})


def generate_heading2_field():
    content = ' '.join(fake.words())

    return generate_field('heading_2', {'content': content})


def generate_heading3_field():
    content = ' '.join(fake.words())

    return generate_field('heading_3', {'content': content})


def generate_raw_html():
    body = """
<div style="border: solid 1px orange; margin: 5px; padding: 5px;">
<p><dl><dt>Block type</dt><dd>Raw <abbr title="Hypertext Markup Language">HTML</abbr></dd>
<dt>Tags used</dt><dd><pre>abbr, pre, dl, dt, dd, progress, label</pre></dd>
</dl></p>
<p>
<label for="completion">How close are we?</label>
<progress id="completion" max="100" value="70"> 70% </progress></p></div>"""
    return generate_field('raw_html', body)


def generate_aligned_captioned_image():
    image = choice(CustomImage.objects.filter(collection__name='Squares')).pk
    caption = '<p>{}</p>'.format(' '.join(fake.words(nb=5)))
    alignment = choice(ALIGNMENT_CHOICES)
    return generate_field(
        'image', {'image': image, 'caption': caption, 'alignment': alignment}
    )


def generate_block_quote():
    text = '<p>{}</p>'.format(fake.sentence())
    source_text = '<p>{}</p>'.format(fake.name())
    source_url = fake.url(schemes=['https'])

    return generate_field(
        'blockquote',
        {'text': text, 'source_text': source_text, 'source_url': source_url},
    )


def generate_list():
    return generate_field('list', fake.words())


class StreamfieldProvider(BaseProvider):
    def streamfield(self, fields=None):
        valid_fields = {
            'heading1': generate_heading1_field,
            'heading2': generate_heading2_field,
            'heading3': generate_heading3_field,
            'rich_text': generate_rich_text,
            'rich_text_paragraph': generate_rich_text_paragraph,
            'bare_image': generate_bare_image,
            'aligned_captioned_image': generate_aligned_captioned_image,
            'raw_html': generate_raw_html,
            'styled_text': generate_styled_text,
            'styled_text_paragraphs': generate_styled_text_paragraphs,
            'blockquote': generate_block_quote,
            'list': generate_list,
        }

        streamfield_data = []
        if not fields:
            raise Exception('no fields found, please provide fields')
        for field in fields:
            if field in valid_fields:
                streamfield_data.append(valid_fields[field]())
            else:
                raise Exception('unknown field: {}'.format(field))

        return json.dumps(streamfield_data)
