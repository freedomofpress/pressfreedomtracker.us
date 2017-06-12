from wagtail.wagtailimages.image_operations import Operation
from willow.registry import registry
from willow.plugins.pillow import PillowImage


# `L` is 8-bit pixels, black and white.
PILLOW_MONOTONE_MODE = 'L'
PILLOW_MONOTONE_MODE_WITH_ALPHA = 'LA'


def pillow_monotone(image):
    if image.has_alpha():
        mode = PILLOW_MONOTONE_MODE_WITH_ALPHA
    else:
        mode = PILLOW_MONOTONE_MODE
    return PillowImage(image.image.convert(mode))


registry.register_operation(PillowImage, 'monotone', pillow_monotone)


class MonotoneOperation(Operation):
    def construct(self):
        pass

    def run(self, willow, image, env):
        willow = willow.monotone()
        return willow
