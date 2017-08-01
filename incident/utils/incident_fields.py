from incident.models import choices

INCIDENT_PAGE_FIELDS = [
    {
        'name': 'date',
        'type': 'date'
    },
    {
        'name': 'affiliation',
        'type': 'char'
    },
    {
        'name': 'city',
        'type': 'char'
    },
    {
        'name': 'state',
        'type': 'pk'
    },
    {
        'name': 'targets',
        'type': 'pk'
    },
    {
        'name': 'tags',
        'type': 'pk'
    },
]

ARREST_FIELDS = [
    {
        'choices': choices.ARREST_STATUS,
        'name': 'arrest_status',
        'type': 'choice'
    },
    {
        'choices': choices.STATUS_OF_CHARGES,
        'name': 'status_of_charges',
        'type': 'choice'
    },
    {
        'name': 'detention_date',
        'type': 'date'
    },
    {
        'name': 'release_date',
        'type': 'date'
    },
    {
        'name': 'unnecessary_use_of_force',
        'category_slug': 'arrest-detention',
        'type': 'bool'
    }
]

LAWSUIT_FIELDS = [
    {
        'name': 'lawsuit_name',
        'type': 'char'
    },
    {
        'name': 'venue',
        'type': 'pk'
    }
]

EQUIPMENT_FIELDS = [
    {
        'name': 'equipment_seized',
        'modifier': 'equipment',
        'type': 'pk',
    },
    {
        'name': 'equipment_broken',
        'type': 'pk',
        'modifier': 'equipment',
    },
    {
        'name': 'status_of_seized_equipment',
        'type': 'choice',
        'choices': choices.STATUS_OF_SEIZED_EQUIPMENT,
    },
    {
        'name': 'is_search_warrant_obtained',
        'type': 'bool',
        'category_slug': 'equipment-search-seizure-or-damage'
    },
    {
        'name': 'actor',
        'type': 'choice',
        'choices': choices.ACTORS,
    },
]

LEAK_PROSECUTIONS_FIELDS = [
    {
        'name': 'charged_under_espionage_act',
        'type': 'bool',
        'category_slug': 'leak-prosecutions',
    }
]

DENIAL_OF_ACCESS_FIELDS = [
    {
        'name': 'politicians_or_public_figures_involved',
        'type': 'pk',
    }
]

BORDER_STOP_FIELDS = [
    {
        'name': 'border_point',
        'type': 'char',
    },
    {
        'name': 'stopped_at_border',
        'type': 'bool',
        'category_slug': 'border-stop-denial-of-entry',
    },
    {
        'name': 'stopped_previously',
        'type': 'bool',
        'category_slug': 'border-stop-denial-of-entry',
    },
    {
        'name': 'target_us_citizenship_status',
        'type': 'choice',
        'choices': choices.CITIZENSHIP_STATUS_CHOICES,
    },
    {
        'name': 'denial_of_entry',
        'type': 'bool',
        'category_slug': 'border-stop-denial-of-entry',
    },
    {
        'name': 'target_nationality',
        'type': 'pk'
    },
    {
        'name': 'did_authorities_ask_for_device_access',
        'type': 'choice',
        'choices': choices.MAYBE_BOOLEAN,
    },
    {
        'name': 'did_authorities_ask_for_social_media_user',
        'type': 'choice',
        'choices': choices.MAYBE_BOOLEAN,
    },
    {
        'name': 'did_authorities_ask_for_social_media_pass',
        'type': 'choice',
        'choices': choices.MAYBE_BOOLEAN,
    },
    {
        'name': 'did_authorities_ask_about_work',
        'type': 'choice',
        'choices': choices.MAYBE_BOOLEAN,
    },
    {
        'name': 'were_devices_searched_or_seized',
        'type': 'choice',
        'choices': choices.MAYBE_BOOLEAN,
    }
]

PHYSICAL_ASSAULT_FIELDS = [
    {
        'name': 'assailant',
        'type': 'choice',
        'choices': choices.ACTORS,
    },
    {
        'name': 'was_journalist_targeted',
        'type': 'choice',
        'choices': choices.MAYBE_BOOLEAN,
    },
]

SUBPOENA_FIELDS = [
    {
        'name': 'subpoena_type',
        'type': 'choice',
        'choices': choices.SUBPOENA_TYPE,
    },
    {
        'name': 'subpoena_status',
        'type': 'choice',
        'choices': choices.SUBPOENA_STATUS,
    },
    {
        'name': 'held_in_contempt',
        'type': 'choice',
        'choices': choices.MAYBE_BOOLEAN,
    },
    {
        'name': 'detention_status',
        'type': 'choice',
        'choices': choices.DETENTION_STATUS,
    },
]

LEGAL_ORDER_FIELDS = [
    {
        'name': 'third_party_in_possession_of_communications',
        'type': 'char',
    },
    {
        'name': 'third_party_business',
        'type': 'choice',
        'choices': choices.THIRD_PARTY_BUSINESS,
    },
    {
        'name': 'legal_order_type',
        'type': 'choice',
        'choices': choices.LEGAL_ORDER_TYPES,
    },

]

PRIOR_RESTRAINT_FIELDS = [
    {
        'name': 'status_of_prior_restraint',
        'type': 'choice',
        'choices': choices.PRIOR_RESTRAINT_STATUS,
    },
]
