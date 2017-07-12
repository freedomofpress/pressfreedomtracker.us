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
        actors,
        # LEAK PROSECUTION
        charged_under_espionage_act,
        # DENIAL OF ACCESS
        politicians_or_public_figures_involved,
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
        self.actors = actors

        # LEAK PROSECUTION
        self.charged_under_espionage_act = charged_under_espionage_act

        # DENIAL OF ACCESS
        self.politicians_or_public_figures_involved = politicians_or_public_figures_involved

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

        if self.arrest_status:
            incidents = self.by_arrest_status(incidents)

        if self.status_of_charges:
            incidents = self.by_status_of_charges(incidents)

        if self.current_charges:
            incidents = self.by_current_charges(incidents)

        if self.dropped_charges:
            incidents = self.by_dropped_charges(incidents)

        # EQUIPMENT
        if self.equipment_seized:
            incidents = self.by_equipment_seized(incidents)

        if self.equipment_broken:
            incidents = self.by_equipment_broken(incidents)

        if self.status_of_seized_equipment:
            incidents = self.by_status_of_seized_equipment(incidents)

        if self.is_search_warrant_obtained:
            incidents = self.by_is_search_warrant_obtained(incidents)

        if self.actors:
            incidents = self.by_actors(incidents)

        # LEAK PROSECUTIONS
        if self.charged_under_espionage_act:
            incidents = self.by_charged_under_espionage_act(incidents)

        # DENIAL OF ACCESS
        if self.politicians_or_public_figures_involved:
            incidents = self.by_politicians_or_public_figures_involved(incidents)

        # BORDER STOP
        if self.border_point:
            incidents = self.by_border_point(incidents)

        if self.stopped_at_border:
            incidents = self.by_stopped_at_border(incidents)

        if self.target_us_citizenship_status:
            incidents = self.by_target_us_citizenship_status(incidents)

        if self.denial_of_entry:
            incidents = self.by_denial_of_entry(incidents)

        if self.stopped_previously:
            incidents = self.by_stopped_previously(incidents)

        if self.target_nationality:
            incidents = self.by_target_nationality(incidents)

        if self.did_authorities_ask_for_device_access:
            incidents = self.by_did_authorities_ask_for_device_access(incidents)

        if self.did_authorities_ask_for_social_media_user :
            incidents = self.by_did_authorities_ask_for_social_media_user (incidents)

        if self.did_authorities_ask_for_social_media_pass :
            incidents = self.by_did_authorities_ask_for_social_media_pass (incidents)

        if self.did_authorities_ask_about_work:
            incidents = self.by_did_authorities_ask_about_work(incidents)


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

    # ARREST/DETENTION Filters
    def by_arrest_status(self, incidents):
        arrest_statuses = validate_choices(self.arrest_status.split(','), choices.ARREST_STATUS)
        if not arrest_statuses:
            return incidents
        return incidents.filter(arrest_status__in=arrest_statuses)

    def by_status_of_charges(self, incidents):
        status_of_charges = validate_choices(self.status_of_charges.split(','), choices.STATUS_OF_CHARGES)
        if not status_of_charges:
            return incidents
        return incidents.filter(status_of_charges__in=status_of_charges)

    def by_current_charges(self, incidents):
        current_charges = validate_integer_list(self.current_charges.split(','))
        if not current_charges:
            return incidents
        return incidents.filter(current_charges__in=current_charges)

    def by_dropped_charges(self, incidents):
        dropped_charges = validate_integer_list(self.dropped_charges.split(','))
        if not dropped_charges:
            return incidents
        return incidents.filter(dropped_charges__in=dropped_charges)

    # EQUIPMENT FILTERS
    def by_equipment_seized(self, incidents):
        equipment_seized = validate_integer_list(self.equipment_seized.split(','))
        if not equipment_seized:
            return incidents
        return incidents.filter(equipment_seized__equipment__in=equipment_seized)

    def by_equipment_broken(self, incidents):
        equipment_broken = validate_integer_list(self.equipment_broken.split(','))
        if not equipment_broken:
            return incidents
        return incidents.filter(equipment_broken__equipment__in=equipment_broken)

    def by_status_of_seized_equipment(self, incidents):
        status_of_seized_equipment = validate_choices(self.status_of_seized_equipment.split(','), choices.STATUS_OF_SEIZED_EQUIPMENT)
        if not status_of_seized_equipment:
            return incidents
        return incidents.filter(status_of_seized_equipment__in=status_of_seized_equipment)

    def by_is_search_warrant_obtained(self, incidents):
        is_search_warrant_obtained = self.is_search_warrant_obtained
        if not is_search_warrant_obtained:
            return incidents
        if is_search_warrant_obtained == 'False':
            # We only want to return incidents for which equipment has been seized
            return incidents.filter(status_of_seized_equipment__isnull=False).filter(is_search_warrant_obtained=False)
        return incidents.filter(is_search_warrant_obtained=is_search_warrant_obtained)

    def by_actors(self, incidents):
        actors = validate_choices(self.actors.split(','), choices.ACTORS)
        if not actors:
            return incidents
        return incidents.filter(actor__in=actors)

    # LEAK PROSECUTIONS
    def by_charged_under_espionage_act(self, incidents):
        if self.charged_under_espionage_act:
            return incidents.filter(charged_under_espionage_act=self.charged_under_espionage_act)

    # DENIAL OF ACCESS
    def by_politicians_or_public_figures_involved(self, incidents):
        politicians_or_public_figures_involved = validate_integer_list(self.politicians_or_public_figures_involved.split(','))
        if not politicians_or_public_figures_involved:
            return incidents
        return incidents.filter(politicians_or_public_figures_involved__in=politicians_or_public_figures_involved)

    # BORDER STOP
    def by_border_point(self, incidents):
        return incidents.filter(border_point__iexact=self.border_point)

    def by_stopped_at_border(self, incidents):
        return incidents.filter(categories__category__slug__iexact="border-stop-denial-of-entry").filter(stopped_at_border=self.stopped_at_border)

    def by_target_us_citizenship_status(self, incidents):
        target_us_citizenship_status = validate_choices(self.target_us_citizenship_status.split(','), choices.CITIZENSHIP_STATUS_CHOICES)
        if not target_us_citizenship_status:
            return incidents
        return incidents.filter(target_us_citizenship_status__in=target_us_citizenship_status)

    def by_denial_of_entry(self, incidents):
        return incidents.filter(categories__category__slug__iexact="border-stop-denial-of-entry").filter(stopped_at_border=self.denial_of_entry)

    def by_stopped_previously(self, incidents):
        return incidents.filter(categories__category__slug__iexact="border-stop-denial-of-entry").filter(stopped_at_border=self.stopped_previously)

    def by_target_nationality(self, incidents):
        target_nationality = validate_integer_list(self.target_nationality.split(','))
        if not target_nationality:
            return incidents
        return incidents.filter(target_nationality__in=target_nationality)

    def by_did_authorities_ask_for_device_access(self, incidents):
        did_authorities_ask_for_device_access = validate_choices(self.did_authorities_ask_for_device_access.split(','), choices.MAYBE_BOOLEAN)
        if not did_authorities_ask_for_device_access:
            return incidents
        return incidents.filter(did_authorities_ask_for_device_access__in=did_authorities_ask_for_device_access)

    def by_did_authorities_ask_for_social_media_user(self, incidents):
        did_authorities_ask_for_social_media_user = validate_choices(self.did_authorities_ask_for_social_media_user.split(','), choices.MAYBE_BOOLEAN)
        if not did_authorities_ask_for_social_media_user:
            return incidents
        return incidents.filter(did_authorities_ask_for_social_media_user__in=did_authorities_ask_for_social_media_user)

    def by_did_authorities_ask_for_social_media_pass(self, incidents):
        did_authorities_ask_for_social_media_pass = validate_choices(self.did_authorities_ask_for_social_media_pass.split(','), choices.MAYBE_BOOLEAN)
        if not did_authorities_ask_for_social_media_pass:
            return incidents
        return incidents.filter(did_authorities_ask_for_social_media_pass__in=did_authorities_ask_for_social_media_pass)

    def by_did_authorities_ask_about_work(self, incidents):
        did_authorities_ask_about_work = validate_choices(self.did_authorities_ask_about_work.split(','), choices.MAYBE_BOOLEAN)
        if not did_authorities_ask_about_work:
            return incidents
        return incidents.filter(did_authorities_ask_about_work__in=did_authorities_ask_about_work)

    def by_were_devices_searched_or_seized(self, incidents):
        were_devices_searched_or_seized = validate_choices(self.were_devices_searched_or_seized.split(','), choices.MAYBE_BOOLEAN)
        if not were_devices_searched_or_seized:
            return incidents
        return incidents.filter(were_devices_searched_or_seized__in=were_devices_searched_or_seized)
