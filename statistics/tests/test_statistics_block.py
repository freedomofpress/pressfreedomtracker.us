from unittest import TestCase, mock

from django.core.exceptions import ValidationError

from statistics.blocks import StatisticsBlock


NUMBERS_MOCK = {
    'no_params': lambda: None,
    'one_param': lambda x: None,
    'two_params': lambda x, y: None,
    'one_optional_param': lambda x=1: None,
    'mixed_params': lambda x, y=1: None,
    'kwargs': lambda **kwargs: None,
}
MAPS_MOCK = {
    'maps_func': lambda: None,
}


# Patch numbers and maps in several places D-:
@mock.patch('statistics.registry.NUMBERS', NUMBERS_MOCK)
@mock.patch('statistics.registry.MAPS', MAPS_MOCK)
@mock.patch('statistics.validators.NUMBERS', NUMBERS_MOCK)
@mock.patch('statistics.validators.MAPS', MAPS_MOCK)
@mock.patch('statistics.blocks.MAPS', MAPS_MOCK)
class CleanTest(TestCase):
    def test_clean_number_stats__number_visualization(self):
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

    def test_clean_number_stats__map_visualization(self):
        block = StatisticsBlock()
        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/blue-table.html',
                'dataset': 'no_params',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'dataset': ['A number dataset cannot be used with a map visualization']})

    def test_clean_map_stats__map_visualization(self):
        block = StatisticsBlock()
        cleaned_value = block.clean({
            'visualization': 'statistics/visualizations/blue-table.html',
            'dataset': 'maps_func',
            'params': '',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'statistics/visualizations/blue-table.html',
            'dataset': 'maps_func',
            'params': '',
        })

    def test_clean_map_stats__number_visualization(self):
        block = StatisticsBlock()
        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'maps_func',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'dataset': ['A map dataset cannot be used with a number visualization']})

    def test_calls_validate_dataset_params(self):
        block = StatisticsBlock()

        with mock.patch('statistics.blocks.validate_dataset_params') as validate_dataset_params:
            block.clean({
                'visualization': 'statistics/visualizations/big-number.html',
                'dataset': 'no_params',
                'params': '200',
            })
            validate_dataset_params.assert_called_once_with('no_params', '200')


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
