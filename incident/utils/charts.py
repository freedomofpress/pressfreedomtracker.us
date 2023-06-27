import json
from urllib import parse

from django.db.models import TextChoices
from django.urls import reverse
from wagtail import blocks

from incident.choices import ACTORS, STATUS_OF_CHARGES


class TreeMapChartValue(blocks.StructValue):
    def branch_field_name(self):
        """Return the name of the field in the dataset that will be
        used to branch/segment the chart."""
        return self.get('group_by').lower()

    def data_url(self):
        """Return the URL to be used to fetch primary data set for the chart."""
        fields = {'categories', 'tags', 'date'}
        fields.add(self.get('group_by').lower())
        return reverse(
            'incidentpage-list',
            kwargs={'version': 'edge'},
        ) + '?' + parse.urlencode(
            {
                'fields': ','.join(fields),
                'format': 'csv',
            }
        )

    def branches(self):
        """Return a data structure that will instruct our front-end
        React component how to get the branches of the tree map
        chart.

        This should be a JSON-encoded string containing a Javascript
        object with the keys "type" (indicating what type of value we
        have), and "value" (containing the actual value).  There are
        two kinds of values here: a URL, and a list.  The URL tells
        our front-end component it needs to perform a request to the
        given URL to get the branches.  The list contains the branches
        as a JS array.

        """
        group_by = self.get('group_by')
        if group_by == TreeMapBranches.CATEGORIES:
            branches_value = {
                'type': 'url',
                'value': reverse(
                    'category-list',
                    kwargs={'version': 'edge'},
                )
            }
        elif group_by == TreeMapBranches.ASSAILANT:
            branches_value = {
                'type': 'list',
                'value': [
                    {'title': title, 'value': value} for
                    value, title in ACTORS
                ]
            }
        elif group_by == TreeMapBranches.STATUS_OF_CHARGES:
            branches_value = {
                'type': 'list',
                'value': [
                    {'title': title, 'value': value} for
                    value, title in STATUS_OF_CHARGES
                ]
            }

        return json.dumps(branches_value)


class TreeMapBranches(TextChoices):
    CATEGORIES = 'CATEGORIES', 'Categories'
    ASSAILANT = 'ASSAILANT', 'Assailant'
    STATUS_OF_CHARGES = 'STATUS_OF_CHARGES', 'Status of Charges'
