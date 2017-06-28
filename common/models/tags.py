from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase


class Tag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_items',
    )
