from unittest import TestCase, mock

from django.core.exceptions import ValidationError

from common.tests.factories import CategoryPageFactory
from statistics.validators import validate_dataset_params


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
class CleanTest(TestCase):
    def test_clean__no_params__gets_none(self):
        validate_dataset_params(dataset='no_params', params='')

    def test_clean__no_params__gets_one_param(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='no_params', params='200')

        self.assertEqual(dict(cm.exception), {'params': ['No parameters may be supplied for this dataset']})

    def test_clean__no_params__gets_two_params(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='no_params', params='200 300')

        self.assertEqual(dict(cm.exception), {'params': ['No parameters may be supplied for this dataset']})

    def test_clean__one_param__gets_none(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='one_param', params='')

        self.assertEqual(dict(cm.exception), {'params': ['At least 1 parameter must be supplied for this dataset']})

    def test_clean__one_param__gets_one_param(self):
        validate_dataset_params(dataset='one_param', params='200')

    def test_clean__one_param__gets_two_params(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='one_param', params='200 300')

        self.assertEqual(dict(cm.exception), {'params': ['At most 1 parameter may be supplied for this dataset']})

    def test_clean__two_params__gets_none(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='two_params', params='')

        self.assertEqual(dict(cm.exception), {'params': ['At least 2 parameters must be supplied for this dataset']})

    def test_clean__two_params__gets_one_param(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='two_params', params='200')

        self.assertEqual(dict(cm.exception), {'params': ['At least 2 parameters must be supplied for this dataset']})

    def test_clean__two_params__gets_two_params(self):
        validate_dataset_params(dataset='two_params', params='200 300')

    def test_clean__two_params__gets_three_params(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='two_params', params='200 300 400')

        self.assertEqual(dict(cm.exception), {'params': ['At most 2 parameters may be supplied for this dataset']})

    def test_clean__one_optional_param__gets_none(self):
        validate_dataset_params(dataset='one_optional_param', params='')

    def test_clean__one_optional_param__gets_one_param(self):
        validate_dataset_params(dataset='one_optional_param', params='200')

    def test_clean__one_optional_param__gets_two_params(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='one_optional_param', params='200 300')

        self.assertEqual(dict(cm.exception), {'params': ['At most 1 parameter may be supplied for this dataset']})

    def test_clean__mixed_params__gets_none(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='mixed_params', params='')

        self.assertEqual(dict(cm.exception), {'params': ['At least 1 parameter must be supplied for this dataset']})

    def test_clean__mixed_params__gets_one_param(self):
        validate_dataset_params(dataset='mixed_params', params='200')

    def test_clean__mixed_params__gets_two_params(self):
        validate_dataset_params(dataset='mixed_params', params='200 300')

    def test_clean__mixed_params__gets_three_params(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='mixed_params', params='200 300 400')

        self.assertEqual(dict(cm.exception), {'params': ['At most 2 parameters may be supplied for this dataset']})

    def test_clean__kwargs__requires_kwargs(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='kwargs', params='200')

        self.assertEqual(dict(cm.exception), {'params': ["Invalid param formatting: '200'"]})

    def test_clean__kwargs__multiple_values(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='kwargs', params='value=200 value=100')

        self.assertEqual(dict(cm.exception), {'params': ["Received multiple values for param 'value'"]})

    def test_clean__kwargs__cleans_with_incident_filter__invalid_param(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(dataset='kwargs', params='value=200')

        self.assertEqual(dict(cm.exception), {'params': ['Invalid parameter provided: value']})

    def test_clean__kwargs__cleans_with_incident_filter__invalid_date_param_value(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(
                dataset='kwargs',
                params='date_lower="2018-01-01" date_upper="2017-01-01"',
            )

        self.assertEqual(dict(cm.exception), {'params': ['date_lower must be less than or equal to date_upper']})

    def test_clean__kwargs__cleans_with_incident_filter__invalid_param_value(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(
                dataset='kwargs',
                params='venue="hello"',
            )

        self.assertEqual(dict(cm.exception), {'params': ['Invalid value for venue: hello']})

    def test_clean__kwargs__cleans_with_incident_filter__variable_param_value(self):
        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(
                dataset='kwargs',
                params='venue=hello',
            )

        self.assertEqual(dict(cm.exception), {'params': ['Value for venue should be wrapped in quotation marks']})

    def test_clean__kwargs__cleans_with_incident_filter__search_param(self):
        validate_dataset_params(
            dataset='kwargs',
            params='search="hello"',
        )

    def test_clean__kwargs__multiple_valid_params(self):
        validate_dataset_params(
            dataset='kwargs',
            params='search="hello" date_lower="2017-01-01"',
        )

    def test_clean_kwargs__combine_multiple_errors(self):
        category = CategoryPageFactory(incident_filters=['arrest_status'])

        with self.assertRaises(ValidationError) as cm:
            validate_dataset_params(
                dataset='kwargs',
                params='categories="{}" arrest_status="hello" circuits="fifty"'.format(
                    category.id,
                ),
            )

        self.assertEqual(dict(cm.exception), {
            'params': [
                'Invalid value for circuits: fifty',
                'Invalid value for arrest_status: hello',
            ],
        })
