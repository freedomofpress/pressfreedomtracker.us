from django.db import models

from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.snippets.models import register_snippet

from modelcluster.models import ClusterableModel

from common.validators import validate_disallow_AND


@register_snippet
class Equipment(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        validate_disallow_AND(value)
        instance = kls(name=value)
        instance.full_clean()
        instance.save()
        return instance

    autocomplete_search_field = "name"

    name = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_disallow_AND],
    )

    panels = [
        FieldRowPanel(
            [
                FieldPanel("name"),
            ]
        )
    ]

    def autocomplete_label(self):
        return str(self)

    def __str__(self):
        return self.name


@register_snippet
class State(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        instance = kls(name=value)
        instance.full_clean()
        instance.save()
        return instance

    autocomplete_search_field = "name"

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    abbreviation = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )

    panels = [
        FieldRowPanel(
            [
                FieldPanel("name"),
                FieldPanel("abbreviation"),
            ]
        ),
    ]

    def autocomplete_label(self):
        return str(self)

    def __str__(self):
        if self.abbreviation:
            return f"{self.name} ({self.abbreviation})"
        return self.name
