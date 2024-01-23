import io
import json
import requests

import PIL.Image
from django.conf import settings
from django.core.files.images import ImageFile
from django.utils.text import slugify

from .types import (
    SnapshotType,
    ChartType,
)


class PregenerationException(Exception):
    pass


def make_request(*, endpoint, file_format, query, stream=False):
    """Internal wrapper function for making a request to the
    pregeneration service."""
    host = settings.CHART_PREGENERATOR['HOST']
    port = settings.CHART_PREGENERATOR['PORT']
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

        # Generate filename
        img_slug = slugify(
            '-'.join(
                # limit to the first 12 characters of value so that it doesn't get too long
                str(v)[:12] for v in query.values() if v
            )
        )
        base_filename = f'{img_slug}_{chart_type}'
        filename = f'{base_filename}.{snapshot_type}'.lower()

        f = io.BytesIO()

        img = PIL.Image.open(response.raw)
        img.save(f, "PNG")
        return ImageFile(f, name=filename)
