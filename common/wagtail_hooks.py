from wagtail.wagtailcore import hooks

from common import image_operations


@hooks.register('register_image_operations')
def register_image_operations():
    return [
        ('monotone', image_operations.MonotoneOperation),
    ]
