from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

class OrganizationPage(Page):
    website = models.URLField(blank=True, null=True)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('website'),
        ImageChooserPanel('logo'),
    ]


class PersonPage(Page):
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    bio = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('bio'),
        ImageChooserPanel('photo'),
    ]



