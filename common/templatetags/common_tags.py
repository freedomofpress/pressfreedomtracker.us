import bleach
from django import template
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
