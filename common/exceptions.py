class PregenerationException(Exception):
    """There was a non-specific problem pregenerating a chart."""
    pass


class InvalidChartType(PregenerationException):
    """The chart type provided is invalid or not supported."""
    pass


class PregenerationAPIFailure(PregenerationException):
    """The pregeneration API could not be reached or failed to give an
    expected response."""
    pass


class ChartNotAvailable(PregenerationException):
    """Failed to either get an existing chart or generate a new one."""
    pass
