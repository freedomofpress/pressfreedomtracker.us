from django.db import models
from wagtail.images.models import Image, AbstractImage, AbstractRendition


class CustomImage(AbstractImage):
    slug = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text='Free-form text. Can be used to store the image filename or other workflow-related information.',
    )
    attribution = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Organization/Photographer. Image description can be set via the caption.'
    )

    admin_form_fields = Image.admin_form_fields + (
        'attribution',
        'slug',
    )


class CustomRendition(AbstractRendition):
    """This class is required by Wagtail when using a custom image.
    """

    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
