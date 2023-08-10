from datetime import datetime, timedelta, timezone
from unittest import mock

import factory
from django.db import IntegrityError
from django.core.files.base import ContentFile
from django.test import TestCase

from common.models.charts import ChartSnapshot
from common.utils.chart_pregenerator.types import (
    ChartType,
    SnapshotType,
)
from common.utils.chart_pregenerator.api import PregenerationException

from .factories import ChartSnapshotFactory


class TestChartSnapshot(TestCase):
    def test_automatically_updates_last_generated_date(self):
        snapshot = ChartSnapshotFactory(
            last_generated=datetime.now(tz=timezone.utc) - timedelta(days=90),
        )
        snapshot.save()
        self.assertAlmostEqual(
            snapshot.last_generated.timestamp(),
            datetime.now(tz=timezone.utc).timestamp(),
            places=2,
        )

    def test_validates_presence_of_svg_data(self):
        with self.assertRaises(IntegrityError):
            ChartSnapshotFactory(
                snapshot_type=SnapshotType.SVG,
                chart_svg=None,
            )

    def test_validates_presence_of_raster_data(self):
        with self.assertRaises(IntegrityError):
            ChartSnapshotFactory(
                snapshot_type=SnapshotType.PNG,
                chart_image=None,
            )

    def test_validates_uniqueness_of_types(self):
        ChartSnapshotFactory(
            svg=True,
            query={'a': 1},
        )

        # Should succeed
        ChartSnapshotFactory(svg=True, query={'a': 2})

        with self.assertRaises(IntegrityError):
            ChartSnapshotFactory(svg=True, query={'a': 1})

    def test_considers_old_snapshots_stale(self):
        old_datetime = datetime.now(tz=timezone.utc) - timedelta(days=90)
        snapshot = ChartSnapshotFactory.build(last_generated=old_datetime)

        self.assertTrue(snapshot.is_stale())

    def test_considers_new_snapshots_not(self):
        new_datetime = datetime.now(tz=timezone.utc) - timedelta(hours=3)
        snapshot = ChartSnapshotFactory.build(last_generated=new_datetime)

        self.assertFalse(snapshot.is_stale())

    @mock.patch('common.models.charts.request_snapshot')
    def test_invokes_chart_generation_api_for_svgs(self, mock_request_snapshot):
        svg_output = """<svg version="1.1" width="300" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="red" /></svg>"""
        mock_request_snapshot.return_value = svg_output

        query = {'query_param': 'value'}
        snapshot = ChartSnapshotFactory(svg=True, query=query)
        snapshot.generate()

        mock_request_snapshot.assert_called_once_with(
            snapshot_type=snapshot.snapshot_type,
            chart_type=snapshot.chart_type,
            query=snapshot.query,
        )
        snapshot.refresh_from_db()
        self.assertEqual(snapshot.chart_svg, svg_output)

    @mock.patch('common.models.charts.request_snapshot')
    def test_invokes_chart_generation_api_for_pngs(self, mock_request_snapshot):
        # Kind of a sideways way to get a `faker` instance via
        # `factory` -- prevents us from having a strict dependency
        # there.
        faker = factory.faker.Faker._get_faker(locale='en-US')
        png_output = faker.image(
            size=(2, 2),
            hue='purple',
            luminosity='bright',
            image_format='png',
        )
        mock_request_snapshot.return_value = ContentFile(png_output)

        query = {'query_param': 'value'}
        snapshot = ChartSnapshotFactory(png=True, query=query)
        snapshot.generate()

        mock_request_snapshot.assert_called_once_with(
            snapshot_type=snapshot.snapshot_type,
            chart_type=snapshot.chart_type,
            query=snapshot.query,
        )
        snapshot.refresh_from_db()
        self.assertEqual(snapshot.chart_image.file.read(), png_output)

    @mock.patch(
        'common.models.charts.request_snapshot',
        side_effect=PregenerationException,
    )
    def test_does_not_update_data_if_generation_api_errors(self, mock_request_snapshot):
        snapshot = ChartSnapshotFactory()
        old_svg = snapshot.chart_svg
        snapshot.generate()
        snapshot.refresh_from_db()
        self.assertEqual(snapshot.chart_svg, old_svg)

    @mock.patch('common.models.charts.request_snapshot')
    def test_does_not_generate_new_rendition_if_one_exists(self, mock_request_snapshot):
        original_snapshot = ChartSnapshotFactory(
            last_generated=datetime.now(tz=timezone.utc) - timedelta(hours=3),
            svg=True,
            chart_type=ChartType.TREEMAP,
            query={'a': 1},
        )

        new_snapshot = ChartSnapshot.get_or_generate(
            chart_type=ChartType.TREEMAP,
            snapshot_type=SnapshotType.SVG,
            query={'a': 1},
        )

        mock_request_snapshot.assert_not_called()
        self.assertEqual(original_snapshot, new_snapshot)

    @mock.patch('common.models.charts.request_snapshot')
    def test_generates_new_rendition_if_one_does_not_exist(self, mock_request_snapshot):
        svg_output = """<svg version="1.1" width="300" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="blue" /></svg>"""
        mock_request_snapshot.return_value = svg_output

        snapshot = ChartSnapshot.get_or_generate(
            chart_type=ChartType.TREEMAP,
            snapshot_type=SnapshotType.SVG,
            query={'a': 1},
        )

        self.assertIsInstance(snapshot, ChartSnapshot)
        self.assertEqual(snapshot.chart_svg, svg_output)

    @mock.patch('common.models.charts.request_snapshot')
    def test_generates_new_rendition_if_existing_one_is_stale(self, mock_request_snapshot):
        svg_output = """<svg version="1.1" width="300" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="green" /></svg>"""
        mock_request_snapshot.return_value = svg_output

        old_datetime = datetime.now(tz=timezone.utc) - timedelta(days=90)
        ChartSnapshotFactory(
            svg=True,
            chart_type=ChartType.TREEMAP,
            query={'a': 1},
        )
        # Need to get around `auto_now` to simulate a stale snapshot
        # with the `update` method that does not trigger it.
        ChartSnapshot.objects.update(last_generated=old_datetime)

        new_snapshot = ChartSnapshot.get_or_generate(
            chart_type=ChartType.TREEMAP,
            snapshot_type=SnapshotType.SVG,
            query={'a': 1},
        )

        self.assertEqual(new_snapshot.chart_svg, svg_output)
