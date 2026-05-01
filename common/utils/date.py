from datetime import date


__all__ = ["format_date"]


def format_date(instance: date) -> str:
    """Formats a date instance into a string that uses AP style."""
    months = [
        "Jan.",
        "Feb.",
        "March",
        "April",
        "May",
        "June",
        "July",
        "Aug.",
        "Sept.",
        "Oct.",
        "Nov.",
        "Dec.",
    ]
    formatted_month = months[instance.month - 1]
    formatted_year = instance.year
    formatted_day = instance.day
    return f"{formatted_month} {formatted_day}, {formatted_year}"
