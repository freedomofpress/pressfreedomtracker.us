import json
from abc import ABCMeta, abstractmethod
from datetime import date
from urllib.parse import urlparse, parse_qs

from django.test import TestCase
from django.urls import reverse

from common.blocks import TreeMapChart
from common.models.charts import ChartSnapshot
from common.tests.factories import ChartSnapshotFactory, CategoryPageFactory
from common.utils.chart_pregenerator.types import (
    ChartType,
    SnapshotType,
)
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
    expected_branches = NotImplementedField

    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory()

    def setUp(self):
        self.tree_map_chart_value = TreeMapChart().to_python({
            'description': 'Test Description',
            'incident_set': {
                'tag': 'test_tag',
                'categories': [self.category.title],
                'lower_date': date(2022, 1, 1),
                'upper_date': date(2023, 1, 1),
            },
            'group_by': self.group_by,
        })
        query = {
            'filterTags': 'test_tag',
            'filterCategories': [self.category.title],
            'dateRange': ['2022-01-01', '2023-01-01'],
            'branches': self.tree_map_chart_value.branches(),
            'branch_field_name': self.tree_map_chart_value.branch_field_name(),
        }
        self.snapshot_svg = ChartSnapshot.objects.create(
            chart_type=ChartType.TREEMAP,
            snapshot_type=SnapshotType.SVG,
            chart_svg='<svg />',
            query=query,
        )
        self.snapshot_png = ChartSnapshotFactory(
            png=True,
            chart_type=ChartType.TREEMAP,
            query=query,
        )

    def test_branch_field_name(self):
        self.assertEqual(
            self.tree_map_chart_value.branch_field_name(),
            self.expected_branch_field_name,
        )

    def test_branches(self):
        self.assertEqual(
            self.tree_map_chart_value.branches(),
            self.expected_branches,
        )

    def test_branches_json_string(self):
        self.assertEqual(
            json.loads(self.tree_map_chart_value.branches_json_string()),
            self.expected_branches,
        )

    def test_data_url_fields_name(self):
        url = urlparse(self.tree_map_chart_value.data_url())
        qs = parse_qs(url.query)
        self.assertIn(
            self.expected_branch_field_name,
            qs['fields'][0],
        )

    def test_png_snapshot_url(self):
        url = self.tree_map_chart_value.png_snapshot_url()
        self.assertEqual(url, self.snapshot_png.chart_image.url)

    def test_svg_snapshot(self):
        self.assertEqual(
            self.tree_map_chart_value.svg_snapshot(),
            self.snapshot_svg.chart_svg,
        )


class TestCategoriesTreeMap(TestTreeMapChartValue, TestCase):
    expected_branch_field_name = 'categories'
    group_by = charts.IncidentBranches.CATEGORIES
    expected_branches = {
        'type': 'url',
        'value': reverse(
            'category-list',
            kwargs={'version': 'edge'},
        )
    }


class TestAssailantTreeMap(TestTreeMapChartValue, TestCase):
    expected_branch_field_name = 'assailant'
    group_by = charts.IncidentBranches.ASSAILANT
    expected_branches = {
        'type': 'list',
        'value': [
            {'title': title, 'value': value} for
            value, title in ACTORS
        ]
    }


class TestChargeStatusTreeMap(TestTreeMapChartValue, TestCase):
    expected_branch_field_name = 'status_of_charges'
    group_by = charts.IncidentBranches.STATUS_OF_CHARGES
    expected_branches = {
        'type': 'list',
        'value': [
            {'title': title, 'value': value} for
            value, title in STATUS_OF_CHARGES
        ]
    }
