from incident.utils.incident_filter import IncidentFilter


def create_incident_filter(**kwargs):
    return IncidentFilter(
        search_text=kwargs.get('search_text', None),
        date_lower=kwargs.get('date_lower', None),
        date_upper=kwargs.get('date_upper', None),
        categories=kwargs.get('categories', None),
        targets=kwargs.get('targets', None),
        affiliation=kwargs.get('affiliation', None),
        state=kwargs.get('state', None),
        tags=kwargs.get('tags', None),
        city=kwargs.get('city', None),

        # Arrest/Detention
        arrest_status=kwargs.get('arrest_status', None),
        status_of_charges=kwargs.get('status_of_charges', None),
        current_charges=kwargs.get('current_charges', None),
        dropped_charges=kwargs.get('dropped_charges', None),
        detention_date_lower=kwargs.get('detention_date_lower', None),
        detention_date_upper=kwargs.get('detention_date_upper', None),
        release_date_lower=kwargs.get('release_date_lower', None),
        release_date_upper=kwargs.get('release_date_upper', None),
        unnecessary_use_of_force=kwargs.get('unnecessary_use_of_force', None),

        # LAWSUIT
        lawsuit_name=kwargs.get('lawsuit_name', None),
        venue=kwargs.get('venue', None),

        # EQUIPMENT
        equipment_seized=kwargs.get('equipment_seized', None),
        equipment_broken=kwargs.get('equipment_broken', None),
        status_of_seized_equipment=kwargs.get('status_of_seized_equipment', None),
        is_search_warrant_obtained=kwargs.get('is_search_warrant_obtained', None),
        actor=kwargs.get('actor', None),

        # BORDER STOP
        border_point=kwargs.get('border_point', None),
        stopped_at_border=kwargs.get('stopped_at_border', None),
        target_us_citizenship_status=kwargs.get('target_us_citizenship_status', None),
        denial_of_entry=kwargs.get('denial_of_entry', None),
        stopped_previously=kwargs.get('stopped_previously', None),
        target_nationality=kwargs.get('target_nationality', None),
        did_authorities_ask_for_device_access=kwargs.get('did_authorities_ask_for_device_access', None),
        did_authorities_ask_for_social_media_user=kwargs.get('did_authorities_ask_for_social_media_user', None),
        did_authorities_ask_for_social_media_pass=kwargs.get('did_authorities_ask_for_social_media_pass', None),
        did_authorities_ask_about_work=kwargs.get('did_authorities_ask_about_work', None),
        were_devices_searched_or_seized=kwargs.get('were_devices_searched_or_seized', None),

        # PHYSICAL ASSAULT
        assailant=kwargs.get('assailant', None),
        was_journalist_targeted=kwargs.get('was_journalist_targeted', None),

        # LEAK PROSECUTION
        charged_under_espionage_act=kwargs.get('charged_under_espionage_act', None),

        # SUBPOENA
        subpoena_type=kwargs.get('subpoena_type', None),
        subpoena_status=kwargs.get('subpoena_status', None),
        held_in_contempt=kwargs.get('held_in_contempt', None),
        detention_status=kwargs.get('detention_status', None),

        # LEGAL ORDER
        third_party_in_possession_of_communications=kwargs.get('third_party_in_possession_of_communications', None),
        third_party_business=kwargs.get('third_party_business', None),
        legal_order_type=kwargs.get('legal_order_type', None),

        # PRIOR RESTRAINT
        status_of_prior_restraint=kwargs.get('status_of_prior_restraint', None),
        # DENIAL OF ACCESS
        politicians_or_public_figures_involved=kwargs.get('politicians_or_public_figures_involved', None),

        # OTHER
        circuits=kwargs.get('circuits', None)
    )
