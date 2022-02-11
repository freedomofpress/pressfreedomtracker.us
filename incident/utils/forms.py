from django import forms

from incident.models import choices


class FilterForm(forms.Form):

    def __init__(self, *args, **kwargs):

        data = kwargs.pop('data', None)
        filters = data.get('filters', None)
        self.id = data.get('id', '')
        self.title = data.get('title', '')
        self.url = data.get('url', '')
        super().__init__(*args, **kwargs)

        if filters:
            for item in filters:
                _type = item.get('type', None)
                name = item.get('name', '')
                label = item.get('title', '')
                field = None
                kwargs = {
                    'required': False,
                    'label': label,
                }

                if _type == 'text' or _type == 'autocomplete':
                    field = forms.CharField

                if _type == 'date':
                    field = forms.DateField
                    kwargs['widget'] = forms.DateInput

                if _type == 'bool':
                    field = forms.ChoiceField
                    kwargs['widget'] = forms.RadioSelect
                    kwargs['choices'] = [('Yes', 'Yes',), ('No', 'No',)]

                if _type == 'choice':
                    field = forms.ChoiceField
                    kwargs['widget'] = forms.Select
                    kwargs['choices'] = [[x[0], x[1].capitalize()] for x in item.get('choices', [])]

                if _type == 'radio':
                    field = forms.ChoiceField
                    kwargs['widget'] = forms.RadioSelect
                    kwargs['choices'] = [[x[0], x[1].capitalize()] for x in choices.MAYBE_BOOLEAN]

                if field:
                    self.fields[name] = field(**kwargs)
                    field.field_type = _type


def get_filter_forms(request, serialized_filters):
    filter_forms = []
    for item in serialized_filters:
        filter_forms.append(
            FilterForm(
                request.GET,
                data=item
            )
        )

    return filter_forms
