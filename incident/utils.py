from datetime import datetime

from psycopg2.extras import DateRange

from incident.models.incident_page import IncidentPage


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
    def __init__(self, search_text, lower_date, upper_date, categories, targets, affiliation, states, tags):
        self.search_text = search_text
        self.lower_date = validate_date(lower_date)
        self.upper_date = validate_date(upper_date)
        self.categories = categories
        self.targets = targets
        self.affiliation = affiliation
        self.states = states
        self.tags = tags

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
