from django import template

from home.models import HomePage


register = template.Library()


@register.filter
def home_page_categories(page):
    return (HomePage.objects
            .ancestor_of(page, inclusive=True)
            .first()
            .categories.all())
