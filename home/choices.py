from django.db.models import TextChoices


# Values match TIME_PRESETS in client/charts/js/lib/utilities.js
class VizTimePeriod(TextChoices):
    SEVEN_DAYS = "SEVEN_DAYS", "Past 7 days"
    FOUR_WEEKS = "FOUR_WEEKS", "Past 4 weeks"
    TWELVE_WEEKS = "TWELVE_WEEKS", "Past 12 weeks"
    SIX_MONTHS = "SIX_MONTHS", "Past six months"
    YEAR = "YEAR", "Current year"
    ALL_TIME = "ALL_TIME", "All time"
