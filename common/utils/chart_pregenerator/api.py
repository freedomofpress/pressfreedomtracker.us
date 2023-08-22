import json
import requests

from django.core.files.images import ImageFile

from .types import (
    SnapshotType,
    ChartType,
)
from .config import settings


class PregenerationException(Exception):
    pass


def make_request(*, endpoint, file_format, query, stream=False):
    """Internal wrapper function for making a request to the
    pregeneration service."""
    host = settings.host
    port = settings.port
    url = f'http://{host}:{port}/{endpoint}.{file_format}'
    try:
        response = requests.get(
            url,
            timeout=5,
            params={'options': json.dumps(query)},
            stream=stream,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise PregenerationException('Failed to reach pregeneration service')
    return response


def request_snapshot(
        snapshot_type: SnapshotType,
        chart_type: ChartType,
        query,
):
    """Request a static image of a given chart type for a given data query.

    May raise ``PregenerationException`` if an error occurs during the
    request.

    :param snapshot_type: The file format for the chart. This
        determines the return value type.
    :param chart_type: The kind of chart to be returned.
    :param query: Dictionary of options to be provided to the chart
        pregeneration service.  The allowed values will vary depending
        on the chart type being requested, and can be viewed in the
        code for the service itself.
    :return: For SVG snapshots, a string containing the SVG content.
        For PNG snapshots, a Django `ImageFile` object containing the
        image file content.

    """
    if chart_type == ChartType.VERTICAL_BAR:
        endpoint = 'bar-chart'
    elif chart_type == ChartType.TREEMAP:
        endpoint = 'treemap-chart'
    elif chart_type == ChartType.BUBBLE_MAP:
        endpoint = 'bubble-map'
    else:
        raise PregenerationException(f'Unknown chart type {chart_type}')

    if snapshot_type == SnapshotType.SVG:
        return make_request(endpoint=endpoint, file_format='svg', query=query).text

    elif snapshot_type == SnapshotType.PNG:
        response = make_request(endpoint=endpoint, file_format='png', query=query, stream=True)
        return ImageFile(response.raw)

    return response
