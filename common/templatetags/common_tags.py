import bleach
import hashlib
import os
from base64 import b64encode
from bs4 import BeautifulSoup
from django import template
from django.core.cache import cache
from django.utils.html import mark_safe
from wagtail.templatetags.wagtailcore_tags import richtext

register = template.Library()


@register.filter
def first_block_of(blocks, type):
    for block in blocks:
        if block.block_type == type:
            return block


@register.filter
def richtext_inline(value):
    "Returns HTML-formatted rich text stripped of block level elements"
    text = richtext(value)
    return mark_safe(bleach.clean(
        text,
        strip=True,
        tags={
            'a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong', 'span'
        }
    ))


@register.filter
def richtext_aside(value):
    "Returns HTML-formatted rich text with span injected in each block level element"
    html_str = richtext(value).__html__()

    # Implicit cache invalidation happens based on the string
    html_str_hash = hashlib.md5(
        html_str.encode('UTF-8'),
        usedforsecurity=False,
    ).hexdigest()
    cache_key = f"aside_html_cache_{html_str_hash}"
    if cache_key in cache:
        return cache.get(cache_key)

    soup = BeautifulSoup(html_str, 'html.parser')
    block_elems = soup.select('[data-block-key]')
    for elem in block_elems:
        if elem.string:
            elem.string.wrap(soup.new_tag('span'))
        elif len(elem.contents):
            new_span = soup.new_tag('span')
            for content in reversed(elem.contents):
                new_span.insert(0, content.extract())
            elem.append(new_span)

    aside_html = mark_safe(str(soup))

    # Setting cache for 1 hour
    cache.set(cache_key, aside_html, 3600)
    return aside_html


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()


@register.filter
def comma_separated_pks(model_list, modifier):
    """Takes a model and an optional modifier and returns a list of primary keys.

    Primarily intended for filtering.
    """
    if modifier:
        pks = [
            str(getattr(model, modifier).pk)
            for model in model_list
        ]
    else:
        pks = [str(model.pk) for model in model_list]

    return ','.join(pks)


@register.filter
def lookup(d, key):
    try:
        return d[key]
    except Exception:
        return ''


@register.filter(is_safe=False)
def add_as_string(value, arg):
    try:
        return str(value) + str(arg)
    except (ValueError, TypeError):
        try:
            return value + arg
        except Exception:
            return ''
