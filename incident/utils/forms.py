from django import forms
from django.utils.text import capfirst
from django.apps import apps

from incident.models import choices


class Datalist(forms.TextInput):
    template_name = 'incident/datalist.html'

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs)
        self.choices = list(choices)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['choices'] = self.choices
        return context


class DatalistField(forms.ChoiceField):
    widget = Datalist
    default_error_messages = {
        'invalid_choice': 'Select a valid choice. %(value)s is not one of the available choices.',
    }

    def __init__(self, *, choices=[], list_name='', **kwargs):
        self.list_name = list_name
        super().__init__(**kwargs)
        self.choices = choices

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['list'] = self.list_name
        attrs['class'] = 'text-field--single'
        attrs['autocomplete'] = 'off'
        return attrs


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

                if _type == 'text':
                    field = forms.CharField
                    kwargs['widget'] = forms.TextInput(
                        attrs={
                            'class': 'text-field--single',
                            'autocomplete': 'off',
                        },
                    )

                if _type == 'autocomplete':
                    field = DatalistField
                    app_label, model_name = item['autocomplete_type'].split('.')
                    model = apps.get_model(app_label, model_name)
                    autocomplete_choices = []
                    for choice in model.objects.all():
                        title_field = getattr(model, 'autocomplete_search_field', 'title')
                        title = getattr(choice, title_field)
                        autocomplete_choices.append(title)
                    kwargs['choices'] = autocomplete_choices
                    kwargs['list_name'] = f'{name}__choices'

                if _type == 'date':
                    field = forms.DateField
                    kwargs['widget'] = forms.DateInput(
                        attrs={'type': 'date'}
                    )
                    kwargs['label'] = label.replace('between', 'before')
                    self.fields[f'{name}_upper'] = field(**kwargs)
                    kwargs['label'] = label.replace('between', 'after')
                    self.fields[f'{name}_lower'] = field(**kwargs)
                    field.field_type = _type
                    continue

                if _type == 'bool':
                    field = forms.ChoiceField
                    kwargs['widget'] = forms.RadioSelect
                    kwargs['choices'] = [('1', 'Yes',), ('0', 'No',)]

                if _type == 'checkbox':
                    field = forms.MultipleChoiceField
                    kwargs['widget'] = forms.CheckboxSelectMultiple
                    kwargs['choices'] = [
                        [value, capfirst(display)] for value, display in item.get('choices', [])
                    ]

                if _type == 'choice':
                    field = forms.ChoiceField
                    kwargs['widget'] = forms.Select
                    kwargs['initial'] = ''
                    kwargs['choices'] = [('', '------')] + [
                        [value, capfirst(display)] for value, display in item.get('choices', [])
                    ]

                if _type == 'radio':
                    field = forms.ChoiceField
                    kwargs['widget'] = forms.RadioSelect
                    kwargs['choices'] = [[x[0], capfirst(x[1])] for x in choices.MAYBE_BOOLEAN]

                if field:
                    self.fields[name] = field(**kwargs)
                    field.field_type = _type


def get_filter_forms(request, serialized_filters):
    filter_forms = []

    # Any filter item with an id other than -1 is a category
    categories = [
        item for item in serialized_filters if item.get('id', -1) != -1
    ]

    for item in serialized_filters:

        # if the item has a filters object then create a form from the item
        if item.get('filters', []):
            filter_forms.append(
                FilterForm(
                    request.GET,
                    data=item
                )
            )

    # if we have category items, create form filter for them
    if categories:
        item = {
            'title': 'Category',
            'filters': [{
                'title': 'Limit to',
                'type': 'checkbox',
                'name': 'categories',
                'choices': [[x.get('id', ''), x.get('title', '')] for x in categories]
            }]

        }
        filter_forms.append(
            FilterForm(
                request.GET,
                data=item
            )
        )

    return filter_forms
