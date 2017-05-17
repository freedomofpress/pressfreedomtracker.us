from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
class Equipment(ClusterableModel):
    name = models.CharField(
        max_length=255,
        unique=True,
    )

    panels = [
        FieldRowPanel([
            FieldPanel('name'),
        ])
    ]

    def __str__(self):
        return self.name
