from django.core.validators import MinValueValidator
from django.db import models

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)


@register_setting
class PrepublicationSettings(BaseGenericSetting):
    class TimespanUnits(models.TextChoices):
        DAY = "DAY", "Days"
        WEEK = "WEEK", "Weeks"
        MONTH = "MONTH", "Months"

    timespan_length = models.PositiveSmallIntegerField(
        verbose_name="length",
        default=30,
        validators=[MinValueValidator(1)],
    )
    timespan_units = models.CharField(
        verbose_name="units",
        max_length=20,
        choices=TimespanUnits,
        default=TimespanUnits.DAY,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("timespan_length"),
                        FieldPanel("timespan_units"),
                    ]
                )
            ],
            heading="Timespan to Display",
            help_text="Prepublication Incidents will only be displayed on the home page and the full listing if they occurred within the given timespan from today's date.",
        )
    ]
