import json
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse, parse_qs

from django.test import TestCase
from django.urls import reverse

from common.blocks import TreeMapChart
from incident.utils import charts
from incident.choices import ACTORS, STATUS_OF_CHARGES


@property
@abstractmethod
def NotImplementedField(self):
    raise NotImplementedError


class TestTreeMapChartValue(metaclass=ABCMeta):
    """Base class for testing tree map chart values"""

    group_by = NotImplementedField
    expected_branch_field_name = NotImplementedField

    def setUp(self):
        self.tree_map_chart_value = TreeMapChart().to_python({
            'description': 'Test Description',
            'group_by': self.group_by,
        })

    def test_branch_field_name(self):
        self.assertEqual(
            self.tree_map_chart_value.branch_field_name(),
            self.expected_branch_field_name,
        )

    def test_data_url_fields_name(self):
        url = urlparse(self.tree_map_chart_value.data_url())
        qs = parse_qs(url.query)
        self.assertIn(
            self.expected_branch_field_name,
            qs['fields'][0],
        )


class TestCategoriesTreeMap(TestTreeMapChartValue, TestCase):
    expected_branch_field_name = 'categories'
    group_by = charts.IncidentBranches.CATEGORIES

    def test_branches(self):
        branches = json.loads(self.tree_map_chart_value.branches())
        self.assertEqual(branches['type'], 'url')
        self.assertEqual(
            branches['value'],
            reverse(
                'category-list',
                kwargs={'version': 'edge'},
            )
        )


class TestAssailantTreeMap(TestTreeMapChartValue, TestCase):
    expected_branch_field_name = 'assailant'
    group_by = charts.IncidentBranches.ASSAILANT

    def test_branches(self):
        expected_branches = {
            'type': 'list',
            'value': [
                {'title': title, 'value': value} for
                value, title in ACTORS
            ]
        }
        branches = json.loads(self.tree_map_chart_value.branches())
        self.assertEqual(branches, expected_branches)


class TestChargeStatusTreeMap(TestTreeMapChartValue, TestCase):
    expected_branch_field_name = 'status_of_charges'
    group_by = charts.IncidentBranches.STATUS_OF_CHARGES

    def test_branches(self):
        expected_branches = {
            'type': 'list',
            'value': [
                {'title': title, 'value': value} for
                value, title in STATUS_OF_CHARGES
            ]
        }
        branches = json.loads(self.tree_map_chart_value.branches())
        self.assertEqual(branches, expected_branches)
