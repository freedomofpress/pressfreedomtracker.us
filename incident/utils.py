from datetime import datetime

from psycopg2.extras import DateRange

from incident.models.incident_page import IncidentPage
from incident.models import choices


def validate_choices(values, choices):
    """Ensure that the values given are valid choices for this field"""
    result = []
    options = [choice[0] for choice in choices]
    for value in values:
        if value in options:
            result.append(value)
    return result


def validate_date(date):
    try:
        valid_date = datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None
    return str(valid_date)


def validate_integer_list(lst):
    """Generate a list of integers from a list of string integers

    Note: strings that cannot be converted into integers are removed
    from the output.
    E.g. ['1', '2', 'a', '3'] --> [1, 2, 3]

    """
    result = []
    for e in lst:
        try:
            result.append(int(e))
        except ValueError:
            continue
    return result


ARREST_FIELDS = [
    dict([('name', 'arrest_status'), ('type', 'choice'), ('choices', choices.ARREST_STATUS)]),
    dict([('name', 'status_of_charges'), ('type', 'choice'), ('choices', choices.STATUS_OF_CHARGES)]),
    dict([('name', 'current_charges'), ('type', 'pk'), ]),
    dict([('name', 'dropped_charges'), ('type', 'pk'), ]),
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
        'name': 'subpoena_subject',
        'type': 'choice',
        'choices': choices.SUBPOENA_SUBJECT,
    },
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


class IncidentFilter(object):
    def __init__(
        self,
        search_text,
        lower_date,
        upper_date,
        categories,
        targets,
        affiliation,
        states,
        tags,
        # ARREST/DETENTION
        arrest_status,
        status_of_charges,
        current_charges,
        dropped_charges,
        # EQUIPMENT
        equipment_seized,
        equipment_broken,
        status_of_seized_equipment,
        is_search_warrant_obtained,
        actor,
        # BORDER STOP
        border_point,
        stopped_at_border,
        stopped_previously,
        target_us_citizenship_status,
        denial_of_entry,
        target_nationality,
        did_authorities_ask_for_device_access,
        did_authorities_ask_for_social_media_user,
        did_authorities_ask_for_social_media_pass,
        did_authorities_ask_about_work,
        were_devices_searched_or_seized,
        # PHYSICAL ASSAULT
        assailant,
        was_journalist_targeted,
        # LEAK PROSECUTION
        charged_under_espionage_act,
        # SUBPOENA
        subpoena_subject,
        subpoena_type,
        subpoena_status,
        held_in_contempt,
        detention_status,
        # LEGAL ORDER
        third_party_in_possession_of_communications,
        third_party_business,
        legal_order_type,
        # PRIOR RESTRAINT
        status_of_prior_restraint,
        # DENIAL OF ACCESS
        politicians_or_public_figures_involved,
    ):
        self.search_text = search_text
        self.lower_date = validate_date(lower_date)
        self.upper_date = validate_date(upper_date)
        self.categories = categories
        self.targets = targets
        self.affiliation = affiliation
        self.states = states
        self.tags = tags

        # Arrest/Detention
        self.arrest_status = arrest_status
        self.status_of_charges = status_of_charges
        self.current_charges = current_charges
        self.dropped_charges = dropped_charges

        # EQUIPMENT
        self.equipment_seized = equipment_seized
        self.equipment_broken = equipment_broken
        self.status_of_seized_equipment = status_of_seized_equipment
        self.is_search_warrant_obtained = is_search_warrant_obtained
        self.actor = actor

        # BORDER STOP
        self.border_point = border_point
        self.stopped_at_border = stopped_at_border
        self.target_us_citizenship_status = target_us_citizenship_status
        self.denial_of_entry = denial_of_entry
        self.stopped_previously = stopped_previously
        self.target_nationality = target_nationality
        self.did_authorities_ask_for_device_access = did_authorities_ask_for_device_access
        self.did_authorities_ask_for_social_media_user = did_authorities_ask_for_social_media_user
        self.did_authorities_ask_for_social_media_pass = did_authorities_ask_for_social_media_pass
        self.did_authorities_ask_about_work = did_authorities_ask_about_work
        self.were_devices_searched_or_seized = were_devices_searched_or_seized

        # PHYSICAL ASSAULT
        self.assailant = assailant
        self.was_journalist_targeted = was_journalist_targeted

        # LEAK PROSECUTION
        self.charged_under_espionage_act = charged_under_espionage_act

        # SUBPOENA
        self.subpoena_subject = subpoena_subject
        self.subpoena_type = subpoena_type
        self.subpoena_status = subpoena_status
        self.held_in_contempt = held_in_contempt
        self.detention_status = detention_status

        # LEGAL ORDER
        self.third_party_in_possession_of_communications = third_party_in_possession_of_communications
        self.third_party_business = third_party_business
        self.legal_order_type = legal_order_type

        # PRIOR RESTRAINT
        self.status_of_prior_restraint = status_of_prior_restraint

        # DENIAL OF ACCESS
        self.politicians_or_public_figures_involved = politicians_or_public_figures_involved

    def create_filters(self, fields, incidents):
        """Creates filters based on dicts for fields

        'name' should be the name of the field AS IT APPEARS ON THE MODEL
        'type' should be 'choice', 'pk', 'bool', or 'char'
        'choices' should match the choices on the model, if any
        'modifier' should be a modifier on the lookup field
        'category_slug' should be the slug of the category for the field. For boolean fields, the filter uses the category, to show correctly interperet falses.
        """
        for field in fields:
            field_name = field['name']

            if getattr(self, field_name):
                if field['type'] == 'choice':
                    validated_field = validate_choices(getattr(self, field_name).split(','), field['choices'])
                    if not validated_field:
                        return incidents

                    kw = {
                        '{0}__in'.format(field_name): validated_field
                    }
                    incidents = incidents.filter(**kw)

                if field['type'] == 'pk':
                    validated_field = validate_integer_list(getattr(self, field_name).split(','))
                    if not validated_field:
                        return incidents

                    if 'modifier' in field.keys():
                        kw = {
                            '{0}__{1}__in'.format(field_name, field['modifier']): validated_field
                        }
                    else:
                        kw = {
                            '{0}__in'.format(field_name): validated_field
                        }
                    return incidents.filter(**kw)

                if field['type'] == 'bool' and getattr(self, field_name):
                    category_kw = {
                        'categories__category__slug__iexact': field['category_slug'],
                    }
                    filter_kw = {
                        field_name: getattr(self, field_name),
                    }

                    return incidents.filter(**category_kw).filter(**filter_kw)

                if field['type'] == 'char':
                    kw = {
                        '{0}'.format(field_name): getattr(self, field_name)
                    }
                    return incidents.filter(**kw)

        return incidents

    def fetch(self):
        incidents = IncidentPage.objects.live()

        if self.lower_date or self.upper_date:
            incidents = self.by_date_range(incidents)

        if self.categories:
            incidents = self.by_categories(incidents)

        if self.targets:
            incidents = self.by_targets(incidents)

        if self.affiliation:
            incidents = self.by_affiliation(incidents)

        if self.states:
            incidents = self.by_states(incidents)

        if self.tags:
            incidents = self.by_tags(incidents)

        # ARREST/DETENTION FILTERS
        incidents = self.create_filters(ARREST_FIELDS, incidents)

        # EQUIPMENT
        incidents = self.create_filters(EQUIPMENT_FIELDS, incidents)

        # BORDER STOP
        incidents = self.create_filters(BORDER_STOP_FIELDS, incidents)

        # PHYSICAL ASSAULT
        incidents = self.create_filters(PHYSICAL_ASSAULT_FIELDS, incidents)

        # LEAK PROSECUTIONS
        incidents = self.create_filters(LEAK_PROSECUTIONS_FIELDS, incidents)

        # SUBPOENA
        incidents = self.create_filters(SUBPOENA_FIELDS, incidents)

        # LEGAL ORDER
        incidents = self.create_filters(LEGAL_ORDER_FIELDS, incidents)

        # PRIOR RESTRAINT
        incidents = self.create_filters(PRIOR_RESTRAINT_FIELDS, incidents)

        # DENIAL OF ACCESS
        incidents = self.create_filters(DENIAL_OF_ACCESS_FIELDS, incidents)

        incidents = incidents.order_by('-date', 'path')

        if self.search_text:
            incidents = self.by_search_text(incidents)

        return incidents

    def by_search_text(self, incidents):
        return incidents.search(self.search_text, order_by_relevance=False)

    def by_date_range(self, incidents):
        return incidents.filter(date__contained_by=DateRange(
            self.lower_date,
            self.upper_date,
        ))

    def by_categories(self, incidents):
        categories = validate_integer_list(self.categories.split(','))
        if not categories:
            return incidents
        return incidents.filter(categories__category__in=categories)

    def by_targets(self, incidents):
        targets = validate_integer_list(self.targets.split(','))
        if not targets:
            return incidents
        return incidents.filter(targets__in=targets)

    def by_affiliation(self, incidents):
        return incidents.filter(affiliation__iexact=self.affiliation)

    def by_states(self, incidents):
        states = validate_integer_list(self.states.split(','))
        if not states:
            return incidents
        return incidents.filter(state__in=states)

    def by_tags(self, incidents):
        tags = validate_integer_list(self.tags.split(','))
        if not tags:
            return incidents
        return incidents.filter(tags__in=tags)
