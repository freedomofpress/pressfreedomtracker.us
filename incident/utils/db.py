from django.db.models import Func, DateField, CharField
from django.contrib.postgres import fields


class MakeDateRange(Func):
    """
    SQL function to calculate the daterange for the month containing a date
    """
    function = 'daterange'
    output_field = fields.DateRangeField()

    # This is needed to make the field behave alongside wagtail
    # search.  If this is not here, wagtail cannot determine the
    # attribute name of the annotation.
    target = type('DateRangeFieldKludge',
                  (fields.DateRangeField,),
                  {'attname': 'fuzzy_date'})()


class CurrentDate(Func):
    """
    SQL function that returns the current date
    """
    template = 'CURRENT_DATE'
    output_field = DateField()


class Left(Func):
    function = "LEFT"
    arity = 2
    output_field = CharField()
