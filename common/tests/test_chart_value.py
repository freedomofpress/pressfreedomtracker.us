from datetime import date

from django.test import TestCase

from common.blocks import (
    BubbleMapChart,
    VerticalBarChart,
)
from common.tests.factories import (
    CategoryPageFactory,
    ChartSnapshotFactory,
)
from common.utils.chart_pregenerator.types import (
    ChartType,
)


class TestVerticalBarChartValue(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory()

    def setUp(self):
        self.vbc_value = VerticalBarChart().to_python(
            {
                "incident_set": {
                    "tag": "test_tag",
                    "categories": [self.category.title],
                    "lower_date": date(2022, 1, 1),
                    "upper_date": date(2023, 1, 1),
                    "states": ["AK"],
                },
                "time_period": "months",
                "description": "Test description",
            }
        )

        query = {
            "filterTags": "test_tag",
            "filterCategories": [self.category.title],
            "dateRange": ["2022-01-01", "2023-01-01"],
            "filterStates": ["AK"],
            "timePeriod": "months",
            "branchFieldName": None,
            "branches": None,
            "groupByTag": None,
        }

        png_query = {
            **query,
            "width": self.vbc_value.NEWSLETTER_WIDTH,
            "height": self.vbc_value.NEWSLETTER_HEIGHT,
            "scale": self.vbc_value.NEWSLETTER_SCALE,
        }
        self.snapshot_png = ChartSnapshotFactory(
            png=True,
            chart_type=ChartType.VERTICAL_BAR,
            query=png_query,
        )
        self.snapshot_svg = ChartSnapshotFactory(
            svg=True,
            chart_type=ChartType.VERTICAL_BAR,
            query=query,
        )

    def test_png_snapshot_url(self):
        url = self.vbc_value.png_snapshot_url()
        self.assertEqual(
            url,
            self.snapshot_png.chart_image.get_rendition("original").full_url,
        )
        # Newsletter emails require an absolute URL. png_snapshot_url() must
        # return one on its own (regression: the newsletter template used to
        # concatenate the site root in front of this, producing a doubled
        # host like "https://hosthttps://media...").
        self.assertTrue(url.startswith("http"))

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
        self.bmc_value = BubbleMapChart().to_python(
            {
                "incident_set": {
                    "tag": "test_tag",
                    "categories": [self.category.title],
                    "states": ["AK"],
                    "lower_date": date(2022, 1, 1),
                    "upper_date": date(2023, 1, 1),
                },
                "group_by": "state",
                "description": "Test description",
            }
        )

        query = {
            "filterTags": "test_tag",
            "filterCategories": [self.category.title],
            "filterStates": ["AK"],
            "dateRange": ["2022-01-01", "2023-01-01"],
            "aggregationLocality": "state",
        }
        png_query = {
            **query,
            "width": self.bmc_value.NEWSLETTER_WIDTH,
            "height": self.bmc_value.NEWSLETTER_HEIGHT,
            "scale": self.bmc_value.NEWSLETTER_SCALE,
        }
        self.snapshot_png = ChartSnapshotFactory(
            png=True,
            chart_type=ChartType.BUBBLE_MAP,
            query=png_query,
        )

        meta_query = {**query, "mini": True, "width": 1200, "height": 630}
        self.snapshot_meta_png = ChartSnapshotFactory(
            png=True,
            chart_type=ChartType.BUBBLE_MAP,
            query=meta_query,
        )

        self.snapshot_svg = ChartSnapshotFactory(
            svg=True,
            chart_type=ChartType.BUBBLE_MAP,
            query=query,
        )

    def test_png_snapshot_url(self):
        url = self.bmc_value.png_snapshot_url()
        self.assertEqual(
            url,
            self.snapshot_png.chart_image.get_rendition("original").full_url,
        )
        # Newsletter emails require an absolute URL. png_snapshot_url() must
        # return one on its own (regression: the newsletter template used to
        # concatenate the site root in front of this, producing a doubled
        # host like "https://hosthttps://media...").
        self.assertTrue(url.startswith("http"))

    def test_png_snapshot_meta_url(self):
        meta_image = self.bmc_value.png_snapshot_meta()
        self.assertEqual(
            meta_image,
            self.snapshot_meta_png.chart_image,
        )

    def test_svg_snapshot(self):
        self.assertEqual(
            self.bmc_value.svg_snapshot(),
            self.snapshot_svg.chart_svg,
        )
