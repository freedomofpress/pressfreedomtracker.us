import operator

from django import forms
from django.db.models import BLANK_CHOICE_DASH
from django.utils.text import capfirst
from django.forms.widgets import NumberInput
from django.apps import apps

import incident.models as incident_models
from incident.models import choices
from common.models import CategoryPage, CommonTag


MAYBE_BOOLEAN_HUMANIZED = [
    ('NOTHING', 'Unknown'),
    ('JUST_TRUE', 'Yes'),
    ('JUST_FALSE', 'No'),
]

BOOLEAN_HUMANIZED = [('1', 'Yes'), ('0', 'No')]


class EmptyChoiceField(forms.ChoiceField):
    """Chioce field with an automatically-provided empty choice."""
    empty_choice = BLANK_CHOICE_DASH

    def __init__(self, *, choices=(), required=False, **kwargs):
        choices = self.empty_choice + list(choices)
        super().__init__(choices=choices, required=required, **kwargs)


# class Datalist(forms.widgets.ChoiceWidget):
#     input_type = 'text'
#     template_name = 'incident/datalist.html'
#     option_template_name = 'django/forms/widgets/select_option.html'
#     add_id_index = False
#     checked_attribute = {'selected': True}
#     option_inherits_attrs = False

#     def get_context(self, name, value, attrs):
#         context = super().get_context(name, value, attrs)
#         context['widget']['attrs']['list'] = f'{name}_datalist'
#         context['widget']['value'] = context['widget']['value'].pop()
#         return context


# class DatalistField(forms.ModelChoiceField):
#     widget = Datalist
#     default_error_messages = {
#         'invalid_choice': 'Select a valid choice. %(value)s is not one of the available choices.',
#     }

#     def __init__(self, required=False, **kwargs):
#         super().__init__(required=required, **kwargs)

#     def widget_attrs(self, widget):
#         attrs = super().widget_attrs(widget)
#         attrs['class'] = 'text-field--single'
#         attrs['autocomplete'] = 'off'
#         return attrs


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


class CategoriesForm(forms.Form):
    title = 'Category'
    categories = forms.ModelMultipleChoiceField(
        label='Limit to',
        queryset=CategoryPage.objects.filter(
            taxonomy_settings__taxonomy_setting__site__is_default_site=True
        ).order_by('taxonomy_settings__sort_order'),
        widget=forms.CheckboxSelectMultiple,
    )


class FilterDateField(forms.DateField):
    widget = forms.DateInput(attrs={'type': 'date'})

    def __init__(self, required=False, **kwargs):
        super().__init__(required=required, **kwargs)


class FilterCharField(forms.CharField):
    def __init__(self, required=False, **kwargs):
        super().__init__(required=required, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['class'] = 'text-field--single'
        attrs['autocomplete'] = 'off'
        return attrs


class BooleanChoiceField(forms.ChoiceField):
    def __init__(self, *, choices=BOOLEAN_HUMANIZED, required=False, **kwargs):
        super().__init__(
            choices=choices,
            widget=forms.RadioSelect,
            required=required,
            **kwargs,
        )


class MaybeBooleanChoiceField(forms.ChoiceField):
    def __init__(self, *, choices=MAYBE_BOOLEAN_HUMANIZED, required=False, **kwargs):
        super().__init__(
            choices=choices,
            widget=forms.RadioSelect,
            required=required,
            **kwargs,
        )


class ArrestForm(forms.Form):
    title = 'Arrest / Criminal Charge'
    release_date_lower = forms.DateField(
        label='Release date after',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    release_date_upper = forms.DateField(
        label='Release date before',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    arrest_status = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.ARREST_STATUS
        ]
    )
    status_of_charges = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.STATUS_OF_CHARGES
        ]
    )
    charges = DatalistField(
        choices=incident_models.Charge.objects.values_list('title'),
        list_name='charges__choices'
        # to_field_name='title',
        # empty_label=None,
    )
    unnecessary_use_of_force = BooleanChoiceField()

    detention_date_lower = FilterDateField(
        label='Detention date after',
    )
    detention_date_upper = FilterDateField(
        label='Detention date before',
    )


class AssaultForm(forms.Form):
    title = 'Assault'
    assailant = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.ACTORS
        ]
    )
    was_journalist_targeted = MaybeBooleanChoiceField(label='Was journalist targeted?')


class BorderStopForm(forms.Form):
    title = 'Border Stop'
    border_point = FilterCharField()
    stopped_at_border = BooleanChoiceField(label='Stopped at border?')
    stopped_previously = BooleanChoiceField(label='Stopped previously?')
    target_nationality = DatalistField(
        choices=incident_models.Nationality.objects.values_list('title'),
        list_name='target_nationality__choices'
        # to_field_name='title',
        # empty_label=None,
    )
    target_us_citizenship_status = EmptyChoiceField(
        label='US Citizenship Status',
        choices=[
            [value, capfirst(display)] for value, display in choices.CITIZENSHIP_STATUS_CHOICES
        ]
    )
    denial_of_entry = BooleanChoiceField(label='Denied entry?')
    did_authorities_ask_about_work = MaybeBooleanChoiceField(label="Did authorities ask intrusive questions about journalist's work?")
    did_authorities_ask_for_device_access = MaybeBooleanChoiceField(
        label='Did authorities ask for device access?',
    )
    were_devices_searched_or_seized = MaybeBooleanChoiceField(
        label='Were devices searched or seized?'
    )
    did_authorities_ask_for_social_media_user = MaybeBooleanChoiceField(
        label='Did authorities ask for social media username?'
    )
    did_authorities_ask_for_social_media_pass = MaybeBooleanChoiceField(
        label='Did authorities ask for social media password?'
    )


class DenialOfAccessForm(forms.Form):
    title = 'Denial of Access'
    politicians_or_public_figures_involved = DatalistField(
        choices=incident_models.PoliticianOrPublic.objects.values_list('title'),
        list_name='politicians_or_public_figures_involved__choices'
        # empty_label=None,
        # to_field_name='title',
    )


class EquipmentDamageForm(forms.Form):
    title = 'Equipment Damage'
    equipment_broken = DatalistField(
        choices=incident_models.Equipment.objects.values_list('name'),
        list_name='equipment_broken__choices'
        # to_field_name='name',
        # empty_label=None,
    )


class EquipmentSearchForm(forms.Form):
    title = 'Equipment Search or Seizure'
    actor = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.ACTORS
        ]
    )
    status_of_seized_equipment = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.STATUS_OF_SEIZED_EQUIPMENT
        ]
    )
    equipment_seized = DatalistField(
        choices=incident_models.Equipment.objects.values_list('name'),
        list_name='equipment_seized__list',
        # to_field_name='name',
        # empty_label=None,
    )
    is_search_warrant_obtained = BooleanChoiceField(label='Search warrant obtained?')


class LeakCaseForm(forms.Form):
    title = 'Leak Case'
    workers_whose_communications_were_obtained = DatalistField(
        choices=incident_models.GovernmentWorker.objects.values_list('title'),
        list_name='workers_whose_communications_were_obtained__choices',
        # empty_label=None,
        # to_field_name='title',
    )
    charged_under_espionage_act = BooleanChoiceField(label='Charged under espionage act?')


class PriorRestraintForm(forms.Form):
    title = 'Prior Restraint'
    status_of_prior_restraint = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.STATUS_OF_PRIOR_RESTRAINT
        ]
    )


class SubpoenaForm(forms.Form):
    title = 'Subpoena/Legal Order'
    subpoena_type = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.SUBPOENA_TYPE
        ]
    )
    subpoena_statuses = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.SUBPOENA_STATUS
        ]
    )
    held_in_contempt = MaybeBooleanChoiceField(label='If subject refused to cooperate, were they held in contempt?')
    detention_status =  EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.DETENTION_STATUS
        ]
    )
    third_party_in_possession_of_communications = FilterCharField()
    third_party_business = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.THIRD_PARTY_BUSINESS
        ]
    )
    legal_order_type = EmptyChoiceField(
        choices=[
            [value, capfirst(display)] for value, display in choices.LEGAL_ORDER_TYPE
        ]
    )


class GeneralForm(forms.Form):
    title = 'General'
    search = FilterCharField(label='Search terms')
    date_lower = FilterDateField(label='Took place after')
    date_upper = FilterDateField(label='Took place before')
    city = FilterCharField(label='City')
    state = DatalistField(
        choices=incident_models.State.objects.values_list('name'),
        list_name='state__choices',
        # to_field_name='name',
        # empty_label=None,
    )
    targeted_journalists = DatalistField(
        label='Targeted any of these journalists',
        choices=incident_models.Journalist.objects.values_list('title'),
        list_name='targeted_journalists__choices',
        # to_field_name='title',
        # empty_label=None,
    )
    targeted_institutions = DatalistField(
        label='Targeted Institutions',
        choices=incident_models.Institution.objects.values_list('title'),
        list_name='targeted_institutions__choices',
        # to_field_name='title',
        # empty_label=None,
    )
    tags = DatalistField(
        label='Has any of these tags',
        choices=CommonTag.objects.values_list('title'),
        list_name='tags__choices',
        # to_field_name='title',
        # empty_label=None,
    )
    case_number = FilterCharField()
    case_statuses = EmptyChoiceField(
        label='Legal Case Status',
        choices=[
            [value, capfirst(display)] for value, display in choices.CASE_STATUS
        ],
    )
    case_type = EmptyChoiceField(
        label='Type of Case',
        choices=[
            [value, capfirst(display)] for value, display in choices.CASE_TYPE
        ],
    )


class FilterForm(forms.Form):

    def __init__(self, *args, **kwargs):

        data = kwargs.pop('data', None)
        filters = data.get('filters', None)
        self.id = data.get('id', '')
        self.title = data.get('title', '')
        self.url = data.get('url', '')
        super().__init__(*args, **kwargs)

        print('-------------------------------------------------------')
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
                    kwargs['queryset'] = model.objects.all()
                    kwargs['empty_label'] = None
                    kwargs['to_field_name'] = getattr(model, 'autocomplete_search_field', 'title')

                if _type == 'date':
                    field = forms.DateField
                    kwargs['widget'] = forms.DateInput(
                        attrs={'type': 'date'}
                    )

                    kwargs['label'] = label.replace('between', 'after')
                    self.fields[f'{name}_lower'] = field(**kwargs)

                    kwargs['label'] = label.replace('between', 'before')
                    self.fields[f'{name}_upper'] = field(**kwargs)

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
                    print(f'{name=}, {field=}')
                    print(f'{kwargs=}')
                    self.fields[name] = field(**kwargs)
                    field.field_type = _type


def get_filter_forms(request, serialized_filters):
    filter_forms = [
        CategoriesForm(request.GET),
        GeneralForm(request.GET),
        ArrestForm(request.GET),
        AssaultForm(request.GET),
        BorderStopForm(request.GET),
        DenialOfAccessForm(request.GET),
        EquipmentDamageForm(request.GET),
        EquipmentSearchForm(request.GET),
        LeakCaseForm(request.GET),
        PriorRestraintForm(request.GET),
        SubpoenaForm(request.GET),
    ]
    return filter_forms

    serialized_filters.sort(key=operator.itemgetter('title'))
    # Any filter item with an id other than -1 is a category
    categories = [
        item for item in serialized_filters if item.get('id', -1) != -1
    ]

    for item in serialized_filters:

        # if the item has a filters object then create a form from the item
        if item.get('filters', []):
            filter_form = FilterForm(request.GET, data=item)
            if item['id'] == -1:
                filter_forms.insert(0, filter_form)
            else:
                filter_forms.append(filter_form)

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
        filter_forms.insert(0, CategoriesForm(request.GET))

    return filter_forms
