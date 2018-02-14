from unittest import TestCase, mock

from django.core.exceptions import ValidationError

from statistics.blocks import StatisticsBlock


NUMBERS_MOCK = {
    'no_params': lambda: None,
    'one_param': lambda x: None,
    'two_params': lambda x, y: None,
    'one_optional_param': lambda x=1: None,
    'mixed_params': lambda x, y=1: None,
}
MAPS_MOCK = {}


@mock.patch('statistics.registry._numbers', NUMBERS_MOCK)
@mock.patch('statistics.registry._maps', MAPS_MOCK)
class CleanTest(TestCase):
    def test_clean__no_params__gets_none(self):
        block = StatisticsBlock()
        cleaned_value = block.clean({
            'visualization': 'big-number.html',
            'dataset': 'no_params',
            'params': '',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'big-number.html',
            'dataset': 'no_params',
            'params': '',
        })

    def test_clean__no_params__gets_one_param(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'no_params',
                'params': '200',
            })

        self.assertEqual(cm.exception.params, {'params': ['No parameters may be supplied for this dataset']})

    def test_clean__no_params__gets_two_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'no_params',
                'params': '200 300',
            })

        self.assertEqual(cm.exception.params, {'params': ['No parameters may be supplied for this dataset']})

    def test_clean__one_param__gets_none(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'one_param',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 1 parameter must be supplied for this dataset']})

    def test_clean__one_param__gets_one_param(self):
        block = StatisticsBlock()

        cleaned_value = block.clean({
            'visualization': 'big-number.html',
            'dataset': 'one_param',
            'params': '200',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'big-number.html',
            'dataset': 'one_param',
            'params': '200',
        })

    def test_clean__one_param__gets_two_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'one_param',
                'params': '200 300',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 1 parameter may be supplied for this dataset']})

    def test_clean__two_params__gets_none(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'two_params',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 2 parameters must be supplied for this dataset']})

    def test_clean__two_params__gets_one_param(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'two_params',
                'params': '200',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 2 parameters must be supplied for this dataset']})

    def test_clean__two_params__gets_two_params(self):
        block = StatisticsBlock()

        cleaned_data = block.clean({
            'visualization': 'big-number.html',
            'dataset': 'two_params',
            'params': '200 300',
        })

        self.assertEqual(cleaned_data, {
            'visualization': 'big-number.html',
            'dataset': 'two_params',
            'params': '200 300',
        })

    def test_clean__two_params__gets_three_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'two_params',
                'params': '200 300 400',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 2 parameters may be supplied for this dataset']})

    def test_clean__one_optional_param__gets_none(self):
        block = StatisticsBlock()

        cleaned_value = block.clean({
            'visualization': 'big-number.html',
            'dataset': 'one_optional_param',
            'params': '',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'big-number.html',
            'dataset': 'one_optional_param',
            'params': '',
        })

    def test_clean__one_optional_param__gets_one_param(self):
        block = StatisticsBlock()

        cleaned_value = block.clean({
            'visualization': 'big-number.html',
            'dataset': 'one_optional_param',
            'params': '200',
        })

        self.assertEqual(cleaned_value, {
            'visualization': 'big-number.html',
            'dataset': 'one_optional_param',
            'params': '200',
        })

    def test_clean__one_optional_param__gets_two_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'one_optional_param',
                'params': '200 300',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 1 parameter may be supplied for this dataset']})

    def test_clean__mixed_params__gets_none(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'mixed_params',
                'params': '',
            })

        self.assertEqual(cm.exception.params, {'params': ['At least 1 parameter must be supplied for this dataset']})

    def test_clean__mixed_params__gets_one_param(self):
        block = StatisticsBlock()

        cleaned_data = block.clean({
            'visualization': 'big-number.html',
            'dataset': 'mixed_params',
            'params': '200',
        })

        self.assertEqual(cleaned_data, {
            'visualization': 'big-number.html',
            'dataset': 'mixed_params',
            'params': '200',
        })

    def test_clean__mixed_params__gets_two_params(self):
        block = StatisticsBlock()

        cleaned_data = block.clean({
            'visualization': 'big-number.html',
            'dataset': 'mixed_params',
            'params': '200 300',
        })

        self.assertEqual(cleaned_data, {
            'visualization': 'big-number.html',
            'dataset': 'mixed_params',
            'params': '200 300',
        })

    def test_clean__mixed_params__gets_three_params(self):
        block = StatisticsBlock()

        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'visualization': 'big-number.html',
                'dataset': 'mixed_params',
                'params': '200 300 400',
            })

        self.assertEqual(cm.exception.params, {'params': ['At most 2 parameters may be supplied for this dataset']})
