class PregenerationException(Exception):
    """There was a non-specific problem pregenerating a chart."""


class InvalidChartType(PregenerationException):
    """The chart type provided is invalid or not supported."""


class PregenerationAPIFailure(PregenerationException):
    """The pregeneration API could not be reached or failed to give an
    expected response."""


class ChartNotAvailable(PregenerationException):
    """Failed to either get an existing chart or generate a new one."""
