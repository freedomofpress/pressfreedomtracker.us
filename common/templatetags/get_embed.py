from django import template

from wagtail.embeds.embeds import get_embed as wagtail_get_embed
from wagtail.embeds.exceptions import EmbedException


register = template.Library()


@register.simple_tag
def get_embed(url):
    try:
        return wagtail_get_embed(url)
    except EmbedException:
        return ""
