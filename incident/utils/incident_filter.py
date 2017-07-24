from datetime import datetime, date
from functools import reduce

from django.db.models import Count
from psycopg2.extras import DateRange

from common.models import CategoryPage
from incident.models.incident_page import IncidentPage
from incident.circuits import STATES_BY_CIRCUIT

from incident.utils.incident_fields import (
    INCIDENT_PAGE_FIELDS,
    ARREST_FIELDS,
    LAWSUIT_FIELDS,
    EQUIPMENT_FIELDS,
    BORDER_STOP_FIELDS,
    PHYSICAL_ASSAULT_FIELDS,
    SUBPOENA_FIELDS,
    LEAK_PROSECUTIONS_FIELDS,
    LEGAL_ORDER_FIELDS,
    PRIOR_RESTRAINT_FIELDS,
    DENIAL_OF_ACCESS_FIELDS
)


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
    return valid_date.date()


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


def validate_bool(string):
    true_list = ['True', 'TRUE', 'true']
    false_list = ['False', 'FALSE', 'false']
    if string in true_list:
        return 'True'
    if string in false_list:
        return 'False'

    return None


def validate_circuits(circuits):
    validated_circuits = []
    for circuit in circuits:
        if circuit in STATES_BY_CIRCUIT.keys():
            validated_circuits.append(circuit)
    return validated_circuits


def get_kwargs(fields, current_kwargs, request):
    for field in fields:
        field_name = field['name']
        if not field['type'] == 'date':
            current_kwargs[field_name] = request.GET.get(field_name)
        else:
            current_kwargs["{0}_lower".format(field_name)] = request.GET.get("{0}_lower".format(field_name))
            current_kwargs["{0}_upper".format(field_name)] = request.GET.get("{0}_upper".format(field_name))
    return current_kwargs


class IncidentFilter(object):
    def __init__(
        # FIELDS
        self,
        search_text,
        lower_date,
        upper_date,
        categories,
        targets,
        affiliation,
        city,
        state,
        tags,
        # ARREST/DETENTION
        arrest_status,
        status_of_charges,
        current_charges,
        dropped_charges,
        detention_date_upper,
        detention_date_lower,
        release_date_upper,
        release_date_lower,
        unnecessary_use_of_force,
        # LAWSUIT
        lawsuit_name,
        venue,
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
        # OTHER
        circuits,
    ):
        self.search_text = search_text
        self.lower_date = validate_date(lower_date)
        self.upper_date = validate_date(upper_date)
        self.categories = categories
        self.targets = targets
        self.affiliation = affiliation
        self.state = state
        self.tags = tags
        self.city = city

        # Arrest/Detention
        self.arrest_status = arrest_status
        self.status_of_charges = status_of_charges
        self.current_charges = current_charges
        self.dropped_charges = dropped_charges
        self.detention_date_lower = validate_date(detention_date_lower)
        self.detention_date_upper = validate_date(detention_date_upper)
        self.release_date_lower = validate_date(release_date_lower)
        self.release_date_upper = validate_date(release_date_upper)
        self.unnecessary_use_of_force = unnecessary_use_of_force

        # LAWSUIT
        self.lawsuit_name = lawsuit_name
        self.venue = venue

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

        # OTHER
        self.circuits = circuits

    def create_filters(self, fields, incidents):
        """Creates filters based on dicts for fields

        'name' should be the name of the field AS IT APPEARS ON THE MODEL
        'type' should be 'choice', 'pk', 'bool', 'date' or 'char'
        'choices' should match the choices on the model, if any
        'modifier' should be a modifier on the lookup field
        'category_slug' should be the slug of the category for the field. For boolean fields, the filter uses the category, to show correctly interperet falses.
        """

        for field in fields:
            field_name = field['name']

            if field['type'] == 'date':
                if getattr(self, '{0}_lower'.format(field_name)) or getattr(self, '{0}_upper'.format(field_name)):
                    lower_date = getattr(self, '{0}_lower'.format(field_name))
                    upper_date = getattr(self, '{0}_upper'.format(field_name))

                    if lower_date == upper_date:
                        kw = {
                            field_name: lower_date
                        }
                        incidents = incidents.filter(**kw)
                    elif lower_date and upper_date and lower_date > upper_date:
                        pass
                    else:
                        kw = {
                            '{0}__contained_by'.format(field_name): DateRange(
                                lower=lower_date,
                                upper=upper_date,
                                bounds='[]'
                            )
                        }
                        incidents = incidents.filter(**kw)

            elif getattr(self, field_name):
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
                        continue

                    if 'modifier' in field.keys():
                        kw = {
                            '{0}__{1}__in'.format(field_name, field['modifier']): validated_field
                        }
                    else:
                        kw = {
                            '{0}__in'.format(field_name): validated_field
                        }
                    incidents = incidents.filter(**kw)

                if field['type'] == 'bool' and getattr(self, field_name):
                    valid_bool = validate_bool(getattr(self, field_name))
                    if valid_bool:
                        category_kw = {
                            'categories__category__slug__iexact': field['category_slug'],
                        }
                        filter_kw = {
                            field_name: valid_bool,
                        }

                        incidents = incidents.filter(**category_kw).filter(**filter_kw)

                if field['type'] == 'char':
                    kw = {
                        '{0}'.format(field_name): getattr(self, field_name)
                    }
                    incidents = incidents.filter(**kw)

        return incidents.prefetch_related('categories__category')

    @classmethod
    def from_request(kls, request):
        kwargs = {
            'search_text': request.GET.get('search'),
            'lower_date': request.GET.get('lower_date'),
            'upper_date': request.GET.get('upper_date'),
            'categories': request.GET.get('categories'),
            'circuits': request.GET.get('circuits'),
        }

        kwargs = reduce(
            (lambda obj, fields: get_kwargs(fields, obj, request)),
            [
                INCIDENT_PAGE_FIELDS,
                ARREST_FIELDS,
                LAWSUIT_FIELDS,
                EQUIPMENT_FIELDS,
                BORDER_STOP_FIELDS,
                PHYSICAL_ASSAULT_FIELDS,
                LEAK_PROSECUTIONS_FIELDS,
                LEGAL_ORDER_FIELDS,
                PRIOR_RESTRAINT_FIELDS,
                SUBPOENA_FIELDS,
                DENIAL_OF_ACCESS_FIELDS,
            ],
            kwargs
        )

        return kls(**kwargs)

    def get_category_options(self):
        return [
            dict(id=page.id, title=page.title)
            for page in CategoryPage.objects.live()
        ]

    def fetch(self):
        """
        Returns (summary, incidents) where summary is a tuple of (label, value)
        pairs of interesting stats for these results and incidents is an
        IncidentPage queryset.

        """

        incidents = IncidentPage.objects.live()

        if self.lower_date or self.upper_date:
            incidents = self.by_date_range(incidents)

        if self.categories:
            incidents = self.by_categories(incidents)

        if self.circuits:
            incidents = self.by_circuits(incidents)

        incidents = reduce(
            (lambda obj, filters: self.create_filters(filters, obj)),
            [
                INCIDENT_PAGE_FIELDS,
                ARREST_FIELDS,
                LAWSUIT_FIELDS,
                EQUIPMENT_FIELDS,
                BORDER_STOP_FIELDS,
                PHYSICAL_ASSAULT_FIELDS,
                LEAK_PROSECUTIONS_FIELDS,
                LEGAL_ORDER_FIELDS,
                PRIOR_RESTRAINT_FIELDS,
                SUBPOENA_FIELDS,
                DENIAL_OF_ACCESS_FIELDS,
            ],
            incidents
        )

        incidents = incidents.order_by('-date', 'path')

        summary = self.summarize(incidents)

        if self.search_text:
            incidents = self.by_search_text(incidents)

        return (summary, incidents)

    def summarize(self, incidents):
        """
        Return a tuple of (label, value) pairs with summary data of the
        incidents.

        The data this chooses to summarize is based on the presence and value
        of particular filters.

        """

        TODAY = date.today()
        THIS_YEAR = TODAY.year
        THIS_MONTH = TODAY.month

        summary = (
            ('Total Incidents', incidents.count),
        )

        # Add counts for this year and this month if non-zero
        incidents_this_year = incidents.filter(date__contained_by=DateRange(
            TODAY.replace(month=1, day=1),
            TODAY.replace(month=12, day=31),
            bounds='[]'
        ))

        incidents_this_month = incidents.filter(date__contained_by=DateRange(
            TODAY.replace(day=1),
            TODAY.replace(month=THIS_MONTH + 1, day=1),
            bounds='[)'
        ))

        if self.search_text:
            num_this_year = incidents_this_year.search(
                self.search_text, order_by_relevance=False
            ).count()
            num_this_month = incidents_this_month.search(
                self.search_text, order_by_relevance=False
            ).count()
        else:
            num_this_year = incidents_this_year.count()
            num_this_month = incidents_this_month.count()

        if num_this_year > 0:
            summary = summary + ((
                'Incidents in {}'.format(THIS_YEAR),
                num_this_year
            ),)

        if num_this_month > 0:
            summary = summary + ((
                'Incidents in {0:%B}'.format(TODAY),
                num_this_month
            ),)

        # If more than one category is included in this set, add a summary item
        # for each category of the form ("Total <Category Name>", <Count>)
        if self.categories is not None:
            category_pks = [int(pk) for pk in self.categories.split(',')]
            if len(category_pks) > 1:
                categories = CategoryPage.objects.filter(
                    pk__in=category_pks
                ).annotate(num_incidents=Count('incidents'))
                for category in categories:
                    summary = summary + ((
                        category.plural_name if category.plural_name else category.title,
                        category.num_incidents,
                    ),)

        return summary

    def by_search_text(self, incidents):
        return incidents.search(self.search_text, order_by_relevance=False)

    def by_date_range(self, incidents):
        if self.lower_date == self.upper_date:
            return incidents.filter(date=self.lower_date)
        if self.lower_date and self.upper_date and self.lower_date > self.upper_date:
            return incidents

        return incidents.filter(date__contained_by=DateRange(
            lower=self.lower_date,
            upper=self.upper_date,
            bounds='[]'
        ))

    def by_categories(self, incidents):
        categories = validate_integer_list(self.categories.split(','))
        if not categories:
            return incidents

        return incidents.filter(categories__category__in=categories).distinct()

    def by_circuits(self, incidents):
        validated_circuits = validate_circuits(self.circuits.split(','))

        states = []
        for circuit in validated_circuits:
            states += STATES_BY_CIRCUIT[circuit]

        return incidents.filter(state__name__in=states)
