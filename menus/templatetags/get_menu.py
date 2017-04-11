from django import template
from menus.models import Menu


register = template.Library()


@register.assignment_tag
def get_menu(slug):
    try:
        menu = Menu.objects.get(slug=slug)
    except:  # Pokemon Exception Handling
        return None
    return menu
