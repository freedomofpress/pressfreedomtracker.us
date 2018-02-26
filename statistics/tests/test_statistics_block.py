from unittest import TestCase, mock

from django.core.exceptions import ValidationError

from common.tests.factories import CategoryPageFactory
from statistics.blocks import StatisticsBlock


NUMBERS_MOCK = {
    'no_params': lambda: None,
    'one_param': lambda x: None,
    'two_params': lambda x, y: None,
    'one_optional_param': lambda x=1: None,
    'mixed_params': lambda x, y=1: None,
    'kwargs': lambda **kwargs: None,
}
MAPS_MOCK = {}


@mock.patch('statistics.registry._numbers', NUMBERS_MOCK)
@mock.patch('statistics.registry._maps', MAPS_MOCK)
class CleanTest(TestCase):
    def test_clean__no_params__gets_none(self):
        block = StatisticsBlock()
        cleaned_value = block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'no_params',
            'params': '',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'no_params',
            'params': '',
        })

    def test_clean__no_params__gets_one_param(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'no_params',
                'params': '200',
            })

        self.assertEqual(cm.exception.params, {'params': ['No parameters may be supplied for this dataset']})

    def test_clean__no_params__gets_two_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'no_params',
                'params': '200 300',
            })

        self.assertEqual(cm.exception.params, {'params': ['No parameters may be supplied for this dataset']})

    def test_clean__one_param__gets_none(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'one_param',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 1 parameter must be supplied for this dataset']})

    def test_clean__one_param__gets_one_param(self):
        block = StatisticsBlock()

        cleaned_value = block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'one_param',
            'params': '200',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'one_param',
            'params': '200',
        })

    def test_clean__one_param__gets_two_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'one_param',
                'params': '200 300',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 1 parameter may be supplied for this dataset']})

    def test_clean__two_params__gets_none(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'two_params',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 2 parameters must be supplied for this dataset']})

    def test_clean__two_params__gets_one_param(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'two_params',
                'params': '200',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 2 parameters must be supplied for this dataset']})

    def test_clean__two_params__gets_two_params(self):
        block = StatisticsBlock()

        cleaned_data = block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'two_params',
            'params': '200 300',
        })

        self.assertEqual(cleaned_data, {
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'two_params',
            'params': '200 300',
        })

    def test_clean__two_params__gets_three_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'two_params',
                'params': '200 300 400',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 2 parameters may be supplied for this dataset']})

    def test_clean__one_optional_param__gets_none(self):
        block = StatisticsBlock()

        cleaned_value = block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'one_optional_param',
            'params': '',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'one_optional_param',
            'params': '',
        })

    def test_clean__one_optional_param__gets_one_param(self):
        block = StatisticsBlock()

        cleaned_value = block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'one_optional_param',
            'params': '200',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'one_optional_param',
            'params': '200',
        })

    def test_clean__one_optional_param__gets_two_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'one_optional_param',
                'params': '200 300',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 1 parameter may be supplied for this dataset']})

    def test_clean__mixed_params__gets_none(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'mixed_params',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 1 parameter must be supplied for this dataset']})

    def test_clean__mixed_params__gets_one_param(self):
        block = StatisticsBlock()

        cleaned_data = block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'mixed_params',
            'params': '200',
        })

        self.assertEqual(cleaned_data, {
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'mixed_params',
            'params': '200',
        })

    def test_clean__mixed_params__gets_two_params(self):
        block = StatisticsBlock()

        cleaned_data = block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'mixed_params',
            'params': '200 300',
        })

        self.assertEqual(cleaned_data, {
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'mixed_params',
            'params': '200 300',
        })

    def test_clean__mixed_params__gets_three_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'mixed_params',
                'params': '200 300 400',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 2 parameters may be supplied for this dataset']})

    def test_clean__kwargs__requires_kwargs(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': '200',
            })

        self.assertEqual(cm.exception.params, {'params': ["Invalid param formatting: '200'"]})

    def test_clean__kwargs__multiple_values(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': 'value=200 value=100',
            })

        self.assertEqual(cm.exception.params, {'params': ["Received multiple values for param 'value'"]})

    def test_clean__kwargs__cleans_with_incident_filter__invalid_param(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': 'value=200',
            })

        self.assertEqual(cm.exception.params, {'params': ['Invalid parameter provided: value']})

    def test_clean__kwargs__cleans_with_incident_filter__invalid_date_param_value(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': 'date_lower="2018-01-01" date_upper="2017-01-01"',
            })

        self.assertEqual(cm.exception.params, {'params': ['date_lower must be less than or equal to date_upper']})

    def test_clean__kwargs__cleans_with_incident_filter__invalid_param_value(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': 'venue="hello"',
            })

        self.assertEqual(cm.exception.params, {'params': ['Invalid value for venue: hello']})

    def test_clean__kwargs__cleans_with_incident_filter__variable_param_value(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': 'venue=hello',
            })

        self.assertEqual(cm.exception.params, {'params': ['Value for venue should be wrapped in quotation marks']})

    def test_clean__kwargs__cleans_with_incident_filter__search_param(self):
        block = StatisticsBlock()

        # Should succeed with no errors.
        block.clean({
            'visualization': 'statistics/visualizations/big-number.html',
            'dataset': 'kwargs',
            'params': 'search="hello"',
        })

    def test_clean__kwargs__multiple_valid_params(self):
        block = StatisticsBlock()

        # Should succeed with no errors.
        try:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': 'search="hello" date_lower="2017-01-01"',
            })
        except ValidationError as exc:
            # unwrap structblock validation magic
            raise ValidationError(exc.params)

    def test_clean_kwargs__combine_multiple_errors(self):
        block = StatisticsBlock()
        category = CategoryPageFactory(incident_filters=['arrest_status'])

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'kwargs',
                'params': 'categories="{}" arrest_status="hello" circuits="fifty"'.format(
                    category.id,
                ),
            })

        self.assertEqual(cm.exception.params, {
            'params': [
                'Invalid value for circuits: fifty',
                'Invalid value for arrest_status: hello',
            ],
        })


class GetContextTest(TestCase):
    def test_renders_statistics__no_params(self):
        block = StatisticsBlock()
        value = {
            'dataset': 'data_tag',
            'params': '',
            'visualization': 'template.html',
        }
        context = block.get_context(value)

        self.assertEqual(context, {
            'template_string': '{% data_tag as data %}{% include "template.html" %}',
            'self': value,
            'value': value,
        })

    def test_renders_statistics__params(self):
        block = StatisticsBlock()
        value = {
            'dataset': 'data_tag',
            'params': 'these are some params',
            'visualization': 'template.html',
        }
        context = block.get_context(value)

        self.assertEqual(context, {
            'template_string': '{% data_tag these are some params as data %}{% include "template.html" %}',
            'self': value,
            'value': value,
        })
