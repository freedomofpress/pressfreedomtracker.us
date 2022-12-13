from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Equipment(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(name=value)

    autocomplete_search_field = 'name'

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    panels = [
        FieldRowPanel([
            FieldPanel('name'),
        ])
    ]

    def autocomplete_label(self):
        return str(self)

    def __str__(self):
        return self.name


@register_snippet
class State(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(name=value)

    autocomplete_search_field = 'name'

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
        FieldRowPanel([
            FieldPanel('name'),
            FieldPanel('abbreviation'),
        ]),
    ]

    def autocomplete_label(self):
        return str(self)

    def __str__(self):
        if self.abbreviation:
            return '{} ({})'.format(self.name, self.abbreviation)
        return self.name
