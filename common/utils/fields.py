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
    'page_ptr',
    'date',
    'exact_date_unknown',
    'body',
    'teaser',
    'teaser_image',
    'image_caption',
    'related_incidents',
    'updates',
    'categories',
    'links',
    'search_image'
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


def get_field_title(field):
    if hasattr(field, 'verbose_name'):
        return field.verbose_name
    elif field.is_relation and hasattr(field.related_model._meta, 'verbose_name'):
        return field.related_model._meta.verbose_name
    elif field.is_relation and hasattr(field, 'related_name'):
        return field.related_name
    else:
        return field.name


def get_field_tuple(field):
    return (field.name, get_field_title(field))


class IncidentPageFieldIterator():
    def __iter__(field):
        # prevents circular import
        from incident.models import IncidentPage
        fields = IncidentPage._meta.get_fields(include_parents=False)
        non_text_fields = list(filter(remove_unwanted_fields, fields))
        for field in non_text_fields:
            yield get_field_tuple(field)


def get_field_type(field):
    if type(field) == ParentalManyToManyField or type(field) == models.fields.related.ManyToOneRel:
        return 'autocomplete'
    elif field.choices:
        # It's a maybe boolean, which we use radio buttons for
        if field.choices[1] == ('JUST_TRUE', 'yes'):
            return 'radio'
        else:
            return 'choice'
    elif type(field) == models.DateField:
        return 'date'
    elif type(field) == models.CharField:
        return 'text'
    elif type(field) == models.BooleanField:
        return 'bool'
    else:
        return str(type(field))


def get_incident_field_dict(field_name):
    # prevents circular import
    from incident.models import IncidentPage
    field_dict = dict()
    fields = IncidentPage._meta.get_fields(include_parents=False)
    field_names = [field.name for field in fields]
    if field_name in field_names:
        field = IncidentPage._meta.get_field(field_name)
        field_dict['title'] = get_field_title(field)
        field_dict['type'] = get_field_type(field)
        field_dict['name'] = field_name

        if field_dict['type'] == 'autocomplete':
            if type(field) == ParentalManyToManyField:
                autocomplete_type = 'incident.{}'.format(field.remote_field.model.__name__)
            elif type(field) == models.fields.related.ManyToOneRel:
                autocomplete_type = field.remote_field.model._autocomplete_model
            else:
                autocomplete_type = None

            field_dict['autocomplete_type'] = autocomplete_type

        return field_dict
    return None
