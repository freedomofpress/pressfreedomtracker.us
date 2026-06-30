from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import pluralize

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)

from dateutil.relativedelta import relativedelta


@register_setting
class PrepublicationSettings(BaseGenericSetting):
    class TimespanUnits(models.TextChoices):
        DAY = "DAY", "Days"
        WEEK = "WEEK", "Weeks"
        MONTH = "MONTH", "Months"

    is_enabled = models.BooleanField(
        default=False,
        verbose_name="Feature is Enabled",
        help_text="If unchecked, unconfirmed incidents will be hidden on the home page and the full listing page will not be accessible.",
    )

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
        FieldPanel("is_enabled"),
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
        ),
    ]

    def get_timespan(self):
        match self.timespan_units:
            case self.TimespanUnits.DAY:
                return relativedelta(days=self.timespan_length)
            case self.TimespanUnits.MONTH:
                return relativedelta(months=self.timespan_length)
            case self.TimespanUnits.WEEK:
                return relativedelta(weeks=self.timespan_length)

    def get_timespan_display(self) -> str:
        return f"{self.timespan_length} {self.timespan_units.lower()}{pluralize(self.timespan_length)}"
