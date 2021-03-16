from rest_framework import serializers

from incident.models import choices


class SummaryField(serializers.RelatedField):
    def to_representation(self, value):
        return value.summary


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]


class EquipmentSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    equipment = serializers.StringRelatedField(read_only=True)


class IncidentLinkSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.URLField()
    publication = serializers.CharField()


class IncidentSerializer(serializers.Serializer):
    title = serializers.CharField()
    slug = serializers.CharField()
    first_published_at = serializers.DateTimeField()
    last_published_at = serializers.DateTimeField()
    latest_revision_created_at = serializers.DateTimeField()

    authors = SummaryField(many=True, read_only=True)
    updates = serializers.StringRelatedField(many=True)
    categories = SummaryField(many=True, read_only=True)
    links = IncidentLinkSerializer(many=True)
    equipment_seized = EquipmentSerializer(many=True, read_only=True)
    equipment_broken = EquipmentSerializer(many=True, read_only=True)
    date = serializers.DateField()
    exact_date_unknown = serializers.BooleanField()
    city = serializers.CharField()
    state = serializers.StringRelatedField()
    body = serializers.SerializerMethodField()
    teaser = serializers.CharField()
    teaser_image = serializers.SerializerMethodField()
    primary_video = serializers.URLField()
    image_caption = serializers.CharField()
    arrest_status = serializers.CharField(source='get_arrest_status_display')
    status_of_charges = serializers.CharField(source='get_status_of_charges_display')
    arresting_authority = serializers.StringRelatedField()
    release_date = serializers.DateField()
    detention_date = serializers.DateField()
    unnecessary_use_of_force = serializers.BooleanField()
    lawsuit_name = serializers.CharField()
    venue = serializers.StringRelatedField(many=True)
    status_of_seized_equipment = serializers.CharField(source='get_status_of_seized_equipment_display')
    is_search_warrant_obtained = serializers.BooleanField()
    actor = serializers.CharField(source='get_actor_display')
    border_point = serializers.CharField()
    stopped_at_border = serializers.BooleanField()
    target_us_citizenship_status = serializers.CharField(source='get_target_us_citizenship_status_display')
    denial_of_entry = serializers.BooleanField()
    stopped_previously = serializers.BooleanField()
    target_nationality = serializers.StringRelatedField(many=True)
    did_authorities_ask_for_device_access = serializers.CharField(source='get_did_authorities_ask_for_device_access_display')
    did_authorities_ask_for_social_media_user = serializers.CharField(source='get_did_authorities_ask_for_social_media_user_display')
    did_authorities_ask_for_social_media_pass = serializers.CharField(source='get_did_authorities_ask_for_social_media_pass_display')
    did_authorities_ask_about_work = serializers.CharField(source='get_did_authorities_ask_about_work_display')
    were_devices_searched_or_seized = serializers.CharField(source='get_were_devices_searched_or_seized_display')
    assailant = serializers.CharField(source='get_assailant_display')
    was_journalist_targeted = serializers.CharField(source='get_was_journalist_targeted_display')
    workers_whose_communications_were_obtained = serializers.StringRelatedField(many=True)
    charged_under_espionage_act = serializers.BooleanField()
    subpoena_type = serializers.CharField(source='get_subpoena_type_display')
    subpoena_statuses = serializers.ListField(
        child=ChoiceField(choices.SUBPOENA_STATUS)
    )
    held_in_contempt = serializers.CharField(source='get_held_in_contempt_display')
    detention_status = serializers.CharField(source='get_detention_status_display')
    third_party_in_possession_of_communications = serializers.CharField()
    third_party_business = serializers.CharField(source='get_third_party_business_display')
    legal_order_type = serializers.CharField(source='get_legal_order_type_display')
    status_of_prior_restraint = serializers.CharField(source='get_status_of_prior_restraint_display')
    targeted_journalists = SummaryField(many=True, read_only=True)
    targeted_institutions = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    current_charges = serializers.StringRelatedField(many=True)
    dropped_charges = serializers.StringRelatedField(many=True)
    politicians_or_public_figures_involved = serializers.StringRelatedField(many=True)

    def get_body(self, obj):
        return str(obj.body)

    def get_teaser_image(self, obj):
        teaser_image = obj.teaser_image
        if teaser_image:
            for rend in teaser_image.renditions.all():
                if rend.filter_spec == 'fill-1330x880':
                    return rend.url
            return teaser_image.get_rendition('fill-1330x880').url
