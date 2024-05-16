import base64
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
        return snapshot.chart_image.get_rendition('original').url

    def svg_snapshot_mini(self):
        options = self.options_schema().dump(self)
        options['mini'] = True
        options['width'] = 655
        options['height'] = 440
        snapshot = ChartSnapshot.get_or_generate(
            chart_type=self.chart_type,
            snapshot_type=SnapshotType.SVG,
            query=options
        )
        return snapshot.chart_svg

    def svg_snapshot_mini_datauri(self):
        return "data:image/svg+xml;base64," + base64.b64encode(self.svg_snapshot_mini().encode()).decode()

    def png_snapshot_meta(self):
        options = self.options_schema().dump(self)
        options['mini'] = True
        options['width'] = 1200
        options['height'] = 630
        snapshot = ChartSnapshot.get_or_generate(
            chart_type=self.chart_type,
            snapshot_type=SnapshotType.PNG,
            query=options
        )
        return snapshot.chart_image
