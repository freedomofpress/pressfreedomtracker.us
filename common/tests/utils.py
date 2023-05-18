from random import choice, randrange, shuffle
import functools

from faker import Faker
from faker.providers import BaseProvider
from wagtail.models import Page

from common.models import CustomImage
from common.choices import BACKGROUND_COLOR_CHOICES
from common.blocks import StyledTextBlock, ALIGNMENT_CHOICES

fake = Faker()


def make_words(minimum=3, maximum=11):
    return ' '.join(fake.words(nb=randrange(minimum, maximum)))


def make_html_string():
    sentence1 = fake.sentence()
    pieces = [
        '<strong>{}</strong>',
        '<em>{}</em>',
        '<a href="{url}">{{}}</a>'.format(
            url=fake.url(schemes=['https']),
        ),
    ]
    words = [make_words().capitalize(), make_words(), make_words()]
    shuffle(pieces)

    sentence2 = ', '.join([
        piece.format(word)
        for piece, word in zip(pieces, words)
    ])
    return f'{sentence1} {sentence2}.'


def generate_field(field_type, value):
    return {'type': field_type, 'value': value, 'id': fake.uuid4()}


def generate_styled_text(as_type='text'):
    background = choice([c[0] for c in BACKGROUND_COLOR_CHOICES])
    text_align = choice([c[0] for c in StyledTextBlock.TEXT_ALIGN_CHOICES])
    font_size = choice([c[0] for c in StyledTextBlock.FONT_SIZE_CHOICES])
    font_family = choice([c[0] for c in StyledTextBlock.FONT_FAMILY_CHOICES])
    text = make_html_string()
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
    image = choice(CustomImage.objects.filter(collection__name='Photos')).pk
    return generate_field('image', image)


def generate_rich_text_paragraph():
    paragraph = '<p>{}</p>'.format(fake.text(max_nb_chars=200))
    return generate_field('rich_text', paragraph)


def generate_rich_text_line():
    return generate_field('rich_text', make_html_string())


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


def generate_heading_field(as_type='heading'):
    content = ' '.join(fake.words()).title()
    return generate_field(as_type, {'content': content})


def generate_raw_html():
    body = """<div style="margin: 0 auto; width: 80%; display: flex; justify-content: center; flex-direction: column; background-color: #ffeedd; color: #111; padding: 10px; border-radius: 10px 100px / 120px;">
<dl><dt>Block type</dt><dd>Raw <abbr title="Hypertext Markup Language">HTML</abbr></dd><dt>Tags used</dt><dd><span style="font-family:monospace;">abbr, dd, div, dl, dt, meter, progress, span, table, td, tr</span></dd></dl>

<table style="width: 66%; margin: 0 auto;">
<tr><td><label for="completion">How close are we?</label></td><td><progress id="completion" max="100" value="{progress}"> {progress}% </progress></td>
<tr><td>Fuel remaining</td><td><meter id="fuel" min="0" max="100" low="33" high="66" optimum="80" value="{fuel}"></meter></td></tr></table></div>"""
    return generate_field('raw_html', body.format(fuel=randrange(0, 101), progress=randrange(0, 101)))


def generate_aligned_captioned_image(as_type='aligned_image'):
    image = choice(CustomImage.objects.filter(collection__name='Photos')).pk
    caption = make_html_string()
    alignment = choice(ALIGNMENT_CHOICES)[0]
    return generate_field(
        as_type, {'image': image, 'caption': caption, 'alignment': alignment}
    )


def generate_block_quote():
    text = '<p>{}</p>'.format(fake.sentence())
    source_text = '<p>{}</p>'.format(fake.name())
    source_url = fake.url(schemes=['https'])

    return generate_field(
        'blockquote',
        {'text': text, 'source_text': source_text, 'source_url': source_url},
    )


def generate_vertical_bar_chart():
    incident_set = {
        'categories': [],
        'tag': None,
        'lower_date': fake.date_between('-2y', '-1y'),
        'upper_date': fake.date_between('-11M'),
    }
    return generate_field(
        'vertical_bar_chart',
        {
            'title': make_words().capitalize(),
            'incident_set': incident_set,
            'description': fake.text(max_nb_chars=200),
        }
    )


def generate_tree_map_chart():
    incident_set = {
        'categories': [],
        'tag': None,
        'lower_date': fake.date_between('-2y', '-1y'),
        'upper_date': fake.date_between('-11M'),
    }
    return generate_field(
        'tree_map_chart',
        {
            'title': make_words().capitalize(),
            'incident_set': incident_set,
            'description': fake.text(max_nb_chars=200),
        }
    )


def generate_aside():
    return generate_field('aside', {'text': make_html_string()})


def generate_list():
    return generate_field('list', fake.words())


def generate_twitter_embed():
    return generate_field(
        'tweet', {'tweet': 'https://twitter.com/SecureDrop/status/1174092303834599424'}
    )


def generate_tabs():
    block_fns = [functools.partial(generate_heading_field, as_type='heading_2'), generate_rich_text_paragraph]
    default_tab = {
        'value': [
            generate_heading_field(as_type='heading_2'),
            generate_rich_text_paragraph(),
            generate_twitter_embed(),
            generate_raw_html()
        ],
        'header': ' '.join(fake.words(nb=2)).title(),
    }

    tabs = [default_tab] + [{
        'header': ' '.join(fake.words(nb=randrange(1, 5))).title(),
        'value': [choice(block_fns)() for i in range(randrange(2, 6))],
    } for _ in range(randrange(1, 4))]

    return generate_field('tabs', tabs)


def generate_info_table_pages():
    num_pages = randrange(2, 11)

    page_links = {
        'cta_label': ' '.join(fake.words(nb=randrange(1, 5))).title(),
        'table_data': [
            {
                'page': page.pk,
                'description': ' '.join(fake.words(nb=randrange(2, 10))).title(),
                'title': ' '.join(fake.words(nb=randrange(2, 10))).title() if i % 2 == 0 else None,
            }
            for i, page in
            enumerate(Page.objects.filter(depth__gt=1).order_by('?')[:num_pages])
        ]
    }

    table = generate_field('page_links', page_links)

    return generate_field(
        'info_table',
        {
            'heading': ' '.join(fake.words(nb=randrange(1, 5))).title(),
            'table': [table],
        }
    )


def generate_info_table_emails():
    num_emails = randrange(2, 11)

    emails = {
        'cta_label': ' '.join(fake.words(nb=randrange(1, 5))).title(),
        'table_data': [
            {
                'email': fake.ascii_safe_email(),
                'title': ' '.join(fake.words(nb=randrange(2, 10))).title(),
            }
            for _ in range(num_emails)
        ]
    }

    table = generate_field('email_addresses', emails)

    return generate_field(
        'info_table',
        {
            'heading': ' '.join(fake.words(nb=randrange(1, 5))).title(),
            'table': [table],
        }
    )


def generate_info_table_plain_text():
    num_text = randrange(2, 11)
    text = {
        'cta_label': ' '.join(fake.words(nb=randrange(1, 5))).title(),
        'table_data': [
            {
                'title': fake.name(),
                'description': ' '.join(fake.words(nb=randrange(6, 16))).title(),
            }
            for _ in range(num_text)
        ]
    }

    table = generate_field('plain_text', text)

    return generate_field(
        'info_table',
        {
            'heading': ' '.join(fake.words(nb=randrange(1, 5))).title(),
            'table': [table],
        }
    )


def generate_info_table_external_links():
    num_links = randrange(2, 11)
    images = CustomImage.objects.filter(
        collection__name='Photos',
    ).order_by('?')[:num_links]

    links = {
        'cta_label': ' '.join(fake.words(nb=randrange(1, 5))).title(),
        'table_data': [
            {
                'url': fake.url(),
                'title': ' '.join(fake.words(nb=randrange(2, 10))).title(),
                'image': images[i].pk,
            }
            for i in range(num_links)
        ]
    }

    table = generate_field('external_links', links)

    return generate_field(
        'info_table',
        {
            'heading': ' '.join(fake.words(nb=randrange(1, 5))).title(),
            'table': [table],
        }
    )


class StreamfieldProvider(BaseProvider):
    def streamfield(self, fields=None):
        valid_fields = {
            'heading1': functools.partial(generate_heading_field, as_type='heading_1'),
            'heading2': functools.partial(generate_heading_field, as_type='heading_2'),
            'heading3': functools.partial(generate_heading_field, as_type='heading_3'),
            'heading': generate_heading_field,
            'rich_text': generate_rich_text,
            'rich_text_paragraph': generate_rich_text_paragraph,
            'rich_text_line': generate_rich_text_line,
            'bare_image': generate_bare_image,
            'aligned_captioned_image': generate_aligned_captioned_image,
            'raw_html': generate_raw_html,
            'styled_text': generate_styled_text,
            'styled_text_paragraphs': generate_styled_text_paragraphs,
            'blockquote': generate_block_quote,
            'list': generate_list,
            'tweet': generate_twitter_embed,
            'tabs': generate_tabs,
            'info_table_pages': generate_info_table_pages,
            'info_table_emails': generate_info_table_emails,
            'info_table_external_links': generate_info_table_external_links,
            'info_table_plain_text': generate_info_table_plain_text,
            'aside': generate_aside,
            'vertical_bar_chart': generate_vertical_bar_chart,
            'tree_map_chart': generate_tree_map_chart,
        }

        streamfield_data = []
        if not fields:
            raise Exception('no fields found, please provide fields')
        for field in fields:
            if field in valid_fields:
                streamfield_data.append(valid_fields[field]())
            else:
                raise Exception('unknown field: {}'.format(field))

        return streamfield_data
