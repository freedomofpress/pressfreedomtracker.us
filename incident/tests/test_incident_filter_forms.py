import operator

from django.test import RequestFactory, TestCase
from django.utils.text import capfirst
from django import forms

from incident.utils.forms import (
    FilterForm,
    get_filter_forms,
    Datalist,
    DatalistField,
)
from incident.models.choices import MAYBE_BOOLEAN
from incident.tests.factories import LawEnforcementOrganizationFactory


def capitalize_choice_labels(choices):
    return [[x[0], capfirst(x[1])] for x in choices]


class FilterFormTest(TestCase):
    def test_filter_type_text(self):
        request = RequestFactory().get('/')
        name = 'search'
        item = {
            'filters': [
                {
                    'title': 'Search terms',
                    'type': 'text',
                    'name': name
                }
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(name), forms.CharField)

    def test_filter_type_date(self):
        request = RequestFactory().get('/')
        name = 'date'
        item = {
            'filters': [
                {
                    'title': 'Took place',
                    'type': 'date',
                    'name': name
                }
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(f'{name}_lower'), forms.DateField)
        self.assertIsInstance(form.fields.get(f'{name}_lower').widget, forms.DateInput)
        self.assertEqual(
            form.fields.get(f'{name}_lower').label,
            'Took place after',
        )
        self.assertIsInstance(form.fields.get(f'{name}_upper'), forms.DateField)
        self.assertIsInstance(form.fields.get(f'{name}_upper').widget, forms.DateInput)
        self.assertEqual(
            form.fields.get(f'{name}_upper').label,
            'Took place before',
        )

    def test_filter_type_bool(self):
        request = RequestFactory().get('/')
        name = 'unnecessary_use_of_force'
        item = {
            'filters': [
                {
                    'title': 'Unnecessary use of force?',
                    'type': 'bool',
                    'name': name
                }
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(name), forms.ChoiceField)
        self.assertIsInstance(form.fields.get(name).widget, forms.RadioSelect)
        self.assertEqual(form.fields.get(name).choices, [('1', 'Yes',), ('0', 'No',)])

    def test_filter_type_checkbox(self):
        request = RequestFactory().get('/')
        name = 'categories'
        choices = [[37, 'Chilling Statement']]
        capitalized = capitalize_choice_labels(choices)
        item = {
            'filters': [
                {
                    'title': 'Category',
                    'type': 'checkbox',
                    'name': name,
                    'choices': choices
                }
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(name), forms.MultipleChoiceField)
        self.assertIsInstance(form.fields.get(name).widget, forms.CheckboxSelectMultiple)
        self.assertEqual(form.fields.get(name).choices, capitalized)

    def test_filter_type_choice(self):
        request = RequestFactory().get('/')
        name = 'status_of_seized_equipment'
        choices = [
            ['UNKNOWN', 'unknown'],
            ['CUSTODY', 'in custody'],
            ['RETURNED_FULL', 'returned in full'],
            ['RETURNED_PART', 'returned in part']
        ]
        capitalized = capitalize_choice_labels(choices)
        capitalized = [('', '------')] + capitalized
        item = {
            'filters': [
                {
                    'title': 'Status of seized equipment',
                    'type': 'choice',
                    'name': name,
                    'choices': choices
                }
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(name), forms.ChoiceField)
        self.assertIsInstance(form.fields.get(name).widget, forms.Select)
        self.assertEqual(form.fields.get(name).choices, capitalized)

    def test_propertly_capitalizes_choices_beginning_with_acronyms(self):
        request = RequestFactory().get('/')
        name = 'target_us_citizenship_status'
        choices = [
            ['US_CITIZEN', 'U.S. citizen'],
            ['PERMANENT_RESIDENT', 'U.S. permanent resident (green card)'],
            ['NON_RESIDENT', 'U.S. non-resident'],
        ]
        expected = [('', '------')] + choices
        item = {
            'filters': [
                {
                    'title': 'Target US Citizenship status',
                    'type': 'choice',
                    'name': name,
                    'choices': choices
                }
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(name), forms.ChoiceField)
        self.assertIsInstance(form.fields.get(name).widget, forms.Select)
        self.assertEqual(form.fields.get(name).choices, expected)

    def test_filter_type_autocomplete_single(self):
        request = RequestFactory().get('/')
        name = 'arresting_authority'
        leo1 = LawEnforcementOrganizationFactory.create(title='Org 1')
        leo2 = LawEnforcementOrganizationFactory.create(title='Org 2')

        expected_choices = [
            leo1.title,
            leo2.title,
        ]
        item = {
            'filters': [
                {
                    'title': 'Arresting authority',
                    'type': 'autocomplete',
                    'name': name,
                    'autocomplete_type': 'incident.LawEnforcementOrganization',
                    'many': False
                },
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(name), DatalistField)
        self.assertIsInstance(form.fields.get(name).widget, Datalist)
        self.assertEqual(form.fields.get(name).choices, expected_choices)

    def test_filter_type_radio(self):
        request = RequestFactory().get('/')
        name = 'was_journalist_targeted'
        capitalized = capitalize_choice_labels(MAYBE_BOOLEAN)
        item = {
            'filters': [
                {
                    'title': 'Was journalist targeted?',
                    'type': 'radio',
                    'name': name,
                    'choices': MAYBE_BOOLEAN
                }
            ]
        }
        form = FilterForm(request.GET, data=item)

        self.assertIsInstance(form.fields.get(name), forms.ChoiceField)
        self.assertIsInstance(form.fields.get(name).widget, forms.RadioSelect)
        self.assertEqual(form.fields.get(name).choices, capitalized)

    def test_get_filter_forms(self):
        request = RequestFactory().get('/')
        name = 'categories'
        choices = [
            [12, 'Prior Restraint'],
            [37, 'Chilling Statement'],
            [38, 'Other Incident']
        ]

        serialized_filters = [
            {
                'title': 'General',
                'id': -1,
                'filters': [{'name': 'search', 'title': 'Search terms', 'type': 'text'}],
            },
            {
                'filters': [
                    {
                        'choices': [
                            ['PENDING', 'pending'],
                            ['DROPPED', 'dropped'],
                            ['STRUCK_DOWN', 'struck down'],
                            ['UPHELD', 'upheld'],
                            ['IGNORED', 'ignored']
                        ],
                        'name': 'status_of_prior_restraint',
                        'title': 'Status of prior restraint',
                        'type': 'choice'
                    },
                ],
                'id': 12,
                'title': 'Prior Restraint',
                'url': '/prior_restraint/',
            },
            {
                'id': 37,
                'title': 'Chilling Statement',
                'url': '/chilling_statement/',
                'filters': []
            },
            {
                'id': 38,
                'title': 'Other Incident',
                'url': '/other_incident/',
                'filters': []
            }
        ]
        form = get_filter_forms(request, serialized_filters)

        self.assertIsInstance(form[0].fields.get(name), forms.MultipleChoiceField)
        self.assertIsInstance(form[0].fields.get(name).widget, forms.CheckboxSelectMultiple)
        self.assertEqual(
            form[0].fields.get(name).choices,
            capitalize_choice_labels(sorted(choices, key=operator.itemgetter(1))),
        )
