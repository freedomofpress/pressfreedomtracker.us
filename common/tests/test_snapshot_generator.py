import json
import xml.etree.ElementTree as ET
from unittest import mock

import requests
from django.core.files.images import ImageFile
from django.test import TestCase

from common.utils.chart_pregenerator.api import (
    request_snapshot,
    PregenerationException,
)
from common.utils.chart_pregenerator.types import (
    SnapshotType,
    ChartType,
)
from incident.tests.factories import IncidentPageFactory


class TestGenerator(TestCase):
    @classmethod
    def setUpTestData(cls):
        IncidentPageFactory()

    @mock.patch('requests.get', side_effect=requests.exceptions.Timeout)
    def test_raises_pregeneration_error_if_service_is_down(self, mock_get):
        with self.assertRaises(PregenerationException):
            request_snapshot(
                snapshot_type=SnapshotType.SVG,
                chart_type=ChartType.VERTICAL_BAR,
                query={},
            )

    def test_raises_pregeneration_error_if_service_is_inaccessible(self):
        failed_response = mock.Mock(ok=False, status_code=500)
        failed_response.raise_for_status = mock.Mock(
            side_effect=requests.exceptions.HTTPError
        )

        with mock.patch('requests.get', return_value=failed_response):
            with self.assertRaises(PregenerationException):
                request_snapshot(
                    snapshot_type=SnapshotType.SVG,
                    chart_type=ChartType.VERTICAL_BAR,
                    query={},
                )

    @mock.patch('requests.get')
    def test_converts_query_to_json_options(self, mock_get):
        query = {
            'filterTags': 'tag1',
            'timePeriod': 'months'
        }

        request_snapshot(
            snapshot_type=SnapshotType.SVG,
            chart_type=ChartType.VERTICAL_BAR,
            query=query,
        )
        first_call = mock_get.call_args_list[0]
        self.assertEqual(
            first_call.kwargs['params'],
            {'options': json.dumps(query)},
        )

    def test_generates_vertical_bar_chart_svgs(self):
        response = request_snapshot(
            snapshot_type=SnapshotType.SVG,
            chart_type=ChartType.VERTICAL_BAR,
            query={},
        )

        # Should contain the appropriate `<svg>` tag
        xml_tree_root = ET.fromstring(response)
        self.assertEqual(xml_tree_root.tag, '{http://www.w3.org/2000/svg}svg')

    def test_generates_vertical_bar_chart_pngs(self):
        output = request_snapshot(
            snapshot_type=SnapshotType.PNG,
            chart_type=ChartType.VERTICAL_BAR,
            query={},
        )
        self.assertIsInstance(output, ImageFile)

    def test_generates_tree_map_chart_svgs(self):
        response = request_snapshot(
            snapshot_type=SnapshotType.SVG,
            chart_type=ChartType.TREEMAP,
            query={},
        )

        # Should contain the appropriate `<svg>` tag
        xml_tree_root = ET.fromstring(response)
        self.assertEqual(xml_tree_root.tag, '{http://www.w3.org/2000/svg}svg')

    def test_generates_tree_map_chart_pngs(self):
        output = request_snapshot(
            snapshot_type=SnapshotType.PNG,
            chart_type=ChartType.TREEMAP,
            query={},
        )
        self.assertIsInstance(output, ImageFile)

    def test_generates_bubble_map_chart_svgs(self):
        response = request_snapshot(
            snapshot_type=SnapshotType.SVG,
            chart_type=ChartType.BUBBLE_MAP,
            query={},
        )

        # Should contain the appropriate `<svg>` tag
        xml_tree_root = ET.fromstring(response)
        self.assertEqual(xml_tree_root.tag, '{http://www.w3.org/2000/svg}svg')

    def test_generates_bubble_map_chart_pngs(self):
        output = request_snapshot(
            snapshot_type=SnapshotType.PNG,
            chart_type=ChartType.BUBBLE_MAP,
            query={},
        )
        self.assertIsInstance(output, ImageFile)
