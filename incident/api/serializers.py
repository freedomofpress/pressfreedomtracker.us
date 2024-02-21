from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from wagtail.rich_text import expand_db_html

from incident import choices


class RichTextCharField(serializers.CharField):
    def to_representation(self, value):
        representation = super().to_representation(value)
        return expand_db_html(representation)


@extend_schema_field(OpenApiTypes.STR)
class SummaryField(serializers.RelatedField):
    def to_representation(self, value):
        return value.summary


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]


class FlatStringRelatedField(serializers.ManyRelatedField):
    """Represents relations as a single string of comma separated string
    values.

    """
    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        kwargs['child_relation'] = serializers.StringRelatedField()
        super().__init__(**kwargs)

    def to_representation(self, obj):
        strings = super().to_representation(obj)
        return ', '.join(strings)


class FlatSummaryField(serializers.ManyRelatedField):
    """Represents relations as a single string of comma separated string
    values.

    """
    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        kwargs['child_relation'] = SummaryField(read_only=True)
        super().__init__(**kwargs)

    def to_representation(self, obj):
        strings = super().to_representation(obj)
        return ', '.join(strings)


class FlatListField(serializers.ListField):
    """Comma-separated string representation of a list field."""

    def to_representation(self, obj):
        obj = super().to_representation(obj)
        return ', '.join([str(element) for element in obj])


class EquipmentAmountSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    equipment = serializers.StringRelatedField(read_only=True)


class IncidentLinkSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.URLField()
    publication = serializers.CharField()


class StateSerializer(serializers.Serializer):
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class EquipmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ItemSerializer(serializers.Serializer):
    """Serializer for incident-related items possessing only primary key and title fields."""
    id = serializers.IntegerField()
    title = serializers.CharField()


class MethodologyItemSerializer(serializers.Serializer):
    label = serializers.CharField()
    description = serializers.CharField()


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    methodology = RichTextCharField()
    plural_name = serializers.CharField()
    slug = serializers.CharField()
    url = serializers.SerializerMethodField()
    methodology_items = MethodologyItemSerializer(many=True)

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        if self.context.get('request'):
            return obj.get_full_url(self.context['request'])
        else:
            return obj.get_full_url()


class VariableFieldSerializer(serializers.Serializer):
    """A serializer that takes a set of field names its context with
    the key `requested_fields` that controls what fields should be
    returned.

    """

    def __init__(self, *args, **kwargs):
        requested_fields = kwargs.get('context', {}).get('requested_fields', set())

        super().__init__(*args, **kwargs)

        if requested_fields:
            # Drop any fields that are not specified in
            # `requested_fields`.
            existing = set(self.fields)
            for field_name in existing - requested_fields:
                self.fields.pop(field_name)


class BaseIncidentSerializer(VariableFieldSerializer):
    title = serializers.CharField()
    url = serializers.SerializerMethodField()
    first_published_at = serializers.DateTimeField()
    last_published_at = serializers.DateTimeField()
    latest_revision_created_at = serializers.DateTimeField()

    date = serializers.DateField()
    exact_date_unknown = serializers.BooleanField()
    city = serializers.CharField()
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()
    body = serializers.SerializerMethodField()
    introduction = serializers.CharField()
    teaser = serializers.CharField()
    teaser_image = serializers.SerializerMethodField()
    primary_video = serializers.URLField()
    image_caption = serializers.CharField()
    arresting_authority = serializers.StringRelatedField()
    arrest_status = serializers.CharField(source='get_arrest_status_display')
    status_of_charges = serializers.CharField(source='get_status_of_charges_display')
    release_date = serializers.DateField()
    detention_date = serializers.DateField()
    unnecessary_use_of_force = serializers.BooleanField()
    case_number = serializers.CharField()
    case_type = serializers.CharField()

    status_of_seized_equipment = serializers.CharField(source='get_status_of_seized_equipment_display')
    is_search_warrant_obtained = serializers.BooleanField()
    actor = serializers.CharField(source='get_actor_display')
    border_point = serializers.CharField()
    target_us_citizenship_status = serializers.CharField(source='get_target_us_citizenship_status_display')
    denial_of_entry = serializers.BooleanField()
    stopped_previously = serializers.BooleanField()

    did_authorities_ask_for_device_access = serializers.CharField(source='get_did_authorities_ask_for_device_access_display')
    did_authorities_ask_about_work = serializers.CharField(source='get_did_authorities_ask_about_work_display')
    assailant = serializers.CharField(source='get_assailant_display')
    was_journalist_targeted = serializers.CharField(source='get_was_journalist_targeted_display')

    charged_under_espionage_act = serializers.BooleanField()
    subpoena_type = serializers.CharField(source='get_subpoena_type_display')

    name_of_business = serializers.CharField()
    third_party_business = serializers.CharField(source='get_third_party_business_display')
    legal_order_type = serializers.CharField(source='get_legal_order_type_display')
    legal_order_venue = serializers.CharField(source='get_legal_order_venue_display')
    status_of_prior_restraint = serializers.CharField(source='get_status_of_prior_restraint_display')
    mistakenly_released_materials = serializers.BooleanField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        if self.context.get('request'):
            return obj.get_full_url(self.context['request'])
        else:
            return obj.get_full_url()

    @extend_schema_field(OpenApiTypes.STR)
    def get_body(self, obj):
        return str(obj.body)

    @extend_schema_field(OpenApiTypes.URI)
    def get_teaser_image(self, obj):
        teaser_image = obj.teaser_image
        if teaser_image:
            for rend in teaser_image.renditions.all():
                if rend.filter_spec == 'fill-1330x880':
                    return rend.url
            return teaser_image.get_rendition('fill-1330x880').url


class IncidentSerializer(BaseIncidentSerializer):
    links = IncidentLinkSerializer(many=True)
    equipment_seized = EquipmentAmountSerializer(many=True, read_only=True)
    equipment_broken = EquipmentAmountSerializer(many=True, read_only=True)
    state = StateSerializer()

    updates = serializers.StringRelatedField(many=True)
    case_statuses = serializers.ListField(
        child=ChoiceField(choices.CASE_STATUS)
    )
    workers_whose_communications_were_obtained = serializers.StringRelatedField(many=True)
    target_nationality = serializers.StringRelatedField(many=True)
    targeted_institutions = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    current_charges = serializers.StringRelatedField(many=True)
    dropped_charges = serializers.StringRelatedField(many=True)
    politicians_or_public_figures_involved = serializers.StringRelatedField(many=True)

    authors = SummaryField(many=True, read_only=True)
    categories = SummaryField(many=True, read_only=True)
    targeted_journalists = SummaryField(many=True, read_only=True)

    subpoena_statuses = serializers.ListField(
        child=ChoiceField(choices.SUBPOENA_STATUS)
    )
    type_of_denial = serializers.ListField(
        child=ChoiceField(choices.TypeOfDenial.choices),
    )


class FlatIncidentSerializer(BaseIncidentSerializer):
    links = FlatStringRelatedField()
    equipment_seized = FlatSummaryField()
    equipment_broken = FlatSummaryField()
    state = serializers.CharField(source='state.abbreviation', default='')

    updates = FlatStringRelatedField()
    case_statuses = FlatListField(
        child=ChoiceField(choices.CASE_STATUS)
    )
    workers_whose_communications_were_obtained = FlatStringRelatedField()
    target_nationality = FlatStringRelatedField()
    targeted_institutions = FlatStringRelatedField()
    tags = FlatStringRelatedField()
    current_charges = FlatStringRelatedField()
    dropped_charges = FlatStringRelatedField()
    politicians_or_public_figures_involved = FlatStringRelatedField()

    authors = FlatSummaryField()
    categories = FlatSummaryField()
    targeted_journalists = FlatSummaryField()

    subpoena_statuses = FlatListField(
        child=ChoiceField(choices.SUBPOENA_STATUS)
    )
    type_of_denial = FlatListField(
        child=ChoiceField(choices.TypeOfDenial.choices)
    )


class CSVIncidentSerializer(VariableFieldSerializer):
    # Ordinary fields directly on IncidentPage/Page
    title = serializers.CharField()
    date = serializers.DateField()
    exact_date_unknown = serializers.BooleanField()
    city = serializers.CharField()
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()
    introduction = serializers.CharField()
    teaser = serializers.CharField()
    primary_video = serializers.URLField()
    image_caption = serializers.CharField()
    release_date = serializers.DateField()
    detention_date = serializers.DateField()
    unnecessary_use_of_force = serializers.BooleanField()
    case_number = serializers.CharField()
    case_type = serializers.CharField()
    is_search_warrant_obtained = serializers.BooleanField()
    border_point = serializers.CharField()
    denial_of_entry = serializers.BooleanField()
    stopped_previously = serializers.BooleanField()
    charged_under_espionage_act = serializers.BooleanField()
    name_of_business = serializers.CharField()
    mistakenly_released_materials = serializers.BooleanField()

    # Choice fields -- data is on IncidentPage but choice text
    # requires an annotation
    status_of_seized_equipment = serializers.CharField(
        source='status_of_seized_equipment_display'
    )
    arrest_status = serializers.CharField(source='arrest_status_display')
    actor = serializers.CharField(source='actor_display')
    target_us_citizenship_status = serializers.CharField(
        source='target_us_citizenship_status_display',
    )
    did_authorities_ask_for_device_access = serializers.CharField(
        source='did_authorities_ask_for_device_access_display',
    )
    did_authorities_ask_about_work = serializers.CharField(
        source='did_authorities_ask_about_work_display',
    )
    assailant = serializers.CharField(source='assailant_display')
    was_journalist_targeted = serializers.CharField(
        source='was_journalist_targeted_display',
    )
    third_party_business = serializers.CharField(
        source='third_party_business_display',
    )
    status_of_prior_restraint = serializers.CharField(
        source='status_of_prior_restraint_display',
    )
    legal_order_venue = serializers.CharField(
        source='legal_order_venue_display',
    )

    # Computed fields requiring an annotation
    arresting_authority = serializers.CharField(source='arresting_authority_title')
    url = serializers.CharField()
    tags = serializers.CharField(source='tag_summary')
    categories = serializers.CharField(source='category_summary')
    state = serializers.CharField(source='state_abbreviation')
    links = serializers.CharField(source='link_summary')
    equipment_broken = serializers.CharField(source='equipment_broken_summary')
    equipment_seized = serializers.CharField(source='equipment_seized_summary')
    status_of_charges = serializers.CharField(source='status_of_charges_summary')
