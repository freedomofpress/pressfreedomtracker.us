from django.db import models
from modelcluster.fields import ParentalManyToManyField

from wagtail.wagtailcore.fields import RichTextField, StreamField

# These fields should not be available for filtering for categories
# some of them are filtered in the General filter set, others are not category-related fields
UNWANTED_FIELDS = [
    'search',
    'affiliation',
    'city',
    'state',
    'targets',
    'tags',
    'lawsuit_name',
    'venue',
    'page_ptr'
    'date',
    'exact_date_unknown',
    'body',
    'teaser',
    'teaser_image',
    'image_caption',
    'related_incidents',
    'updates',
]


def remove_unwanted_fields(field):
    if (
        isinstance(field, RichTextField) or
        isinstance(field, StreamField) or
        isinstance(field, models.TextField) or
        field.name in UNWANTED_FIELDS
    ):
        return False
    return True


def get_field_tuple(field):
    if hasattr(field, 'verbose_name'):
        return (field.name, field.verbose_name)
    elif field.is_relation and hasattr(field, 'related_name'):
        return (field.name, field.related_name)
    else:
        return (field.name, field.name)


class IncidentPageFieldIterator():
    def __iter__(field):
        # prevents circular import
        from incident.models import IncidentPage
        fields = IncidentPage._meta.get_fields(include_parents=False)
        non_text_fields = list(filter(remove_unwanted_fields, fields))
        for field in non_text_fields:
            yield get_field_tuple(field)


def get_incident_field_dict(field_name):
    # prevents circular import
    from incident.models import IncidentPage
    fields = IncidentPage._meta.get_fields(include_parents=False)
    field_names = [field.name for field in fields]
    if field_name in field_names:
        field = next((field for field in fields if field_name == field.name), None)
        if hasattr(field, 'verbose_name'):
            title = field.verbose_name
        elif field.is_relation and hasattr(field, 'related_name'):
            title = field.related_name
        else:
            title = field.name

        if type(field) == ParentalManyToManyField:
            field_type = 'autocomplete'
            autocomplete_type = 'incident.{}'.format(field.remote_field.model.__name__)
        elif type(field) == models.fields.related.ManyToOneRel:
            field_type = 'autocomplete'
            autocomplete_type = field.remote_field.model._autocomplete_model
        elif len(field.choices) > 0:
            # It's a maybe boolean, which we use radio buttons for
            if field.choices[1] == ('JUST_TRUE', 'yes'):
                field_type = 'radio'
            else:
                field_type = 'choice'

        elif type(field) == models.DateField:
            field_type = 'date'
        elif type(field) == models.CharField:
            field_type = 'text'
        elif type(field) == models.BooleanField:
            field_type = 'bool'
        else:
            field_type = str(type(field))

        field_dict = dict(
            name=field_name,
            type=field_type,
            title=title
        )
        if field_type == 'autocomplete':
            field_dict['autocomplete_type'] = autocomplete_type

        return field_dict
    return None
