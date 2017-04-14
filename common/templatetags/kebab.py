from django import template

register = template.Library()

@register.filter(name='kebab')
def kebab(string):
    """Converts a string to lowercase and kebab-case"""
    return string.lower().replace(' ', '-')
