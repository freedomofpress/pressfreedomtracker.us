import json
from wagtail import blocks

from common.models.charts import ChartSnapshot
from common.utils.chart_pregenerator.types import SnapshotType


class ChartValue(blocks.StructValue):
    def svg_snapshot(self):
        snapshot = ChartSnapshot.get_or_generate(
            chart_type=self.chart_type,
            snapshot_type=SnapshotType.SVG,
            query=self.options_schema().dump(self)
        )
        return snapshot.chart_svg

    def png_snapshot_url(self):
        snapshot = ChartSnapshot.get_or_generate(
            chart_type=self.chart_type,
            snapshot_type=SnapshotType.PNG,
            query=self.options_schema().dump(self)
        )
        return snapshot.chart_image.url

    def png_snapshot_mini_url(self):
        options = self.options_schema().dump(self)
        options['mini'] = True
        options['width'] = 655
        options['height'] = 440
        snapshot = ChartSnapshot.get_or_generate(
            chart_type=self.chart_type,
            snapshot_type=SnapshotType.PNG,
            query=options
        )
        return snapshot.chart_image.url

    def png_snapshot_meta_url(self):
        options = self.options_schema().dump(self)
        options['mini'] = True
        options['width'] = 1200
        options['height'] = 630
        snapshot = ChartSnapshot.get_or_generate(
            chart_type=self.chart_type,
            snapshot_type=SnapshotType.PNG,
            query=options
        )
        return snapshot.chart_image.url
