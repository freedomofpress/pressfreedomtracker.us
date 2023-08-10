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
