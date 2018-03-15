from unittest import mock

from django.test import TestCase

from common.models.pages import StatisticsItem


class CleanTest(TestCase):
    def test_clean_calls_validate_dataset_params(self):
        item = StatisticsItem(
            dataset='hello',
            params='200',
        )

        with mock.patch('common.models.pages.validate_dataset_params') as validate_dataset_params:
            item.clean()
            validate_dataset_params.assert_called_once_with('hello', '200')
