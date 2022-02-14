from django.test import RequestFactory, TestCase
from django import forms

from incident.utils.forms import FilterForm, get_filter_forms
from incident.models.choices import MAYBE_BOOLEAN


def capitalize_choice_labels(choices):
    return [[x[0], x[1].capitalize()] for x in choices]


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
                    'title': 'Took place between',
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
        self.assertEqual(form.fields.get(name).choices, [('Yes', 'Yes',), ('No', 'No',)])

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
        serialized_filters = [
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
