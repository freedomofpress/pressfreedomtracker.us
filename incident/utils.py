from psycopg2.extras import DateRange

from incident.models.incident_page import IncidentPage


class IncidentFilter(object):
    def __init__(self, search_text, lower_date, upper_date, categories):
        self.search_text = search_text
        self.lower_date = lower_date
        self.upper_date = upper_date
        self.categories = categories

    def fetch(self):
        incidents = IncidentPage.objects.live()

        if self.lower_date and self.upper_date:
            incidents = self.by_date_range(incidents)

        if self.categories:
            incidents = self.by_categories(incidents)

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
        return incidents.filter(categories__in=self.categories)
