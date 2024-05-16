from django.db.models import TextChoices


class ChartType(TextChoices):
    VERTICAL_BAR = 'VERTICAL_BAR', 'Vertical Bar Chart'
    TREEMAP = 'TREEMAP', 'Treemap'
    BUBBLE_MAP = 'BUBBLE_MAP', 'Bubble Map'


class SnapshotType(TextChoices):
    PNG = 'PNG', 'Raster (PNG)'
    SVG = 'SVG', 'SVG'
