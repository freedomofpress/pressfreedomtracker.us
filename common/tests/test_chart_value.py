from datetime import date

from django.test import TestCase

from common.tests.factories import (
    ChartSnapshotFactory,
    CategoryPageFactory,
)
from common.blocks import (
    VerticalBarChart,
    BubbleMapChart,
)
from common.utils.chart_pregenerator.types import (
    ChartType,
)


class TestVerticalBarChartValue(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory()

    def setUp(self):
        self.vbc_value = VerticalBarChart().to_python({
            'incident_set': {
                'tag': 'test_tag',
                'categories': [self.category.title],
                'lower_date': date(2022, 1, 1),
                'upper_date': date(2023, 1, 1),
            },
            'time_period': 'months',
            'description': 'Test description',
        })

        query = {
            'filterTags': 'test_tag',
            'filterCategories': [self.category.title],
            'dateRange': ['2022-01-01', '2023-01-01'],
            'timePeriod': 'months',
        }

        self.snapshot_png = ChartSnapshotFactory(
            png=True,
            chart_type=ChartType.VERTICAL_BAR,
            query=query,
        )
        self.snapshot_svg = ChartSnapshotFactory(
            svg=True,
            chart_type=ChartType.VERTICAL_BAR,
            query=query,
        )

    def test_png_snapshot_url(self):
        url = self.vbc_value.png_snapshot_url()
        self.assertEqual(url, self.snapshot_png.chart_image.url)

    def test_svg_snapshot(self):
        self.assertEqual(
            self.vbc_value.svg_snapshot(),
            self.snapshot_svg.chart_svg,
        )


class TestBubbleMapValue(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory()

    def setUp(self):
        self.bmc_value = BubbleMapChart().to_python({
            'incident_set': {
                'tag': 'test_tag',
                'categories': [self.category.title],
                'lower_date': date(2022, 1, 1),
                'upper_date': date(2023, 1, 1),
            },
            'group_by': 'state',
            'description': 'Test description',
        })

        query = {
            'filterTags': 'test_tag',
            'filterCategories': [self.category.title],
            'dateRange': ['2022-01-01', '2023-01-01'],
            'aggregationLocality': 'state',
        }
        self.snapshot_png = ChartSnapshotFactory(
            png=True,
            chart_type=ChartType.BUBBLE_MAP,
            query=query,
        )
        self.snapshot_svg = ChartSnapshotFactory(
            svg=True,
            chart_type=ChartType.BUBBLE_MAP,
            query=query,
        )

    def test_png_snapshot_url(self):
        url = self.bmc_value.png_snapshot_url()
        self.assertEqual(url, self.snapshot_png.chart_image.url)

    def test_svg_snapshot(self):
        self.assertEqual(
            self.bmc_value.svg_snapshot(),
            self.snapshot_svg.chart_svg,
        )
