from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey


class CurrentChargesTag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_current_charges',
    )


class DroppedChargesTag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_dropped_charges',
    )


class TargetsTag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_targets',
    )


class NationalityTag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_nationalities',
    )


class TargetsCommunicationsObtainedTag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_targets_communications_obtained',
    )


class PoliticiansOrPublicTag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_politicians_or_public',
    )
