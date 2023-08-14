import json
from urllib import parse

from django.db.models import TextChoices
from django.urls import reverse

from common.utils.charts import ChartValue
from common.utils.chart_pregenerator.types import ChartType
from common.models.charts import (
    TreeMapOptionsSchema,
    VerticalBarChartOptionsSchema,
)
from incident.choices import ACTORS, STATUS_OF_CHARGES


class BranchingChartValue(ChartValue):
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

    def branches_json_string(self):
        """JSON-encoded string containing the ``branches`` data."""
        return json.dumps(self.branches())

    def branches(self):
        """Return a data structure that will instruct our front-end
        React component how to get the branches of the tree map
        chart.

        This should be a dictionary with the keys "type" (indicating
        what type of value we have), and "value" (containing the
        actual value).  There are two kinds of values here: a URL, and
        a list.  The URL tells our front-end component it needs to
        perform a request to the given URL to get the branches.  The
        list contains the branches as a python list.

        """
        group_by = self.get('group_by')
        if group_by == IncidentBranches.CATEGORIES:
            branches_value = {
                'type': 'url',
                'value': reverse(
                    'category-list',
                    kwargs={'version': 'edge'},
                )
            }
        elif group_by == IncidentBranches.ASSAILANT:
            branches_value = {
                'type': 'list',
                'value': [
                    {'title': title, 'value': value} for
                    value, title in ACTORS
                ]
            }
        elif group_by == IncidentBranches.STATUS_OF_CHARGES:
            branches_value = {
                'type': 'list',
                'value': [
                    {'title': title, 'value': value} for
                    value, title in STATUS_OF_CHARGES
                ]
            }

        return branches_value


class TreeMapChartValue(BranchingChartValue):
    options_schema = TreeMapOptionsSchema
    chart_type = ChartType.TREEMAP


class VerticalBarChartValue(BranchingChartValue):
    options_schema = VerticalBarChartOptionsSchema
    chart_type = ChartType.VERTICAL_BAR


class IncidentBranches(TextChoices):
    CATEGORIES = 'CATEGORIES', 'Categories'
    ASSAILANT = 'ASSAILANT', 'Assailant'
    STATUS_OF_CHARGES = 'STATUS_OF_CHARGES', 'Status of Charges'
