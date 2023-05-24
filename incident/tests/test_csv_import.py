from django.test import TestCase

from incident.utils.csv import DateColumn, ColumnNotFound


class RequiredDateColumnTestCase(TestCase):
    def setUp(self):
        self.column = DateColumn(name='field1', required=True)

    def test_requires_the_data_field_to_be_present(self):
        with self.assertRaises(ColumnNotFound):
            self.column.get_value({'field2': 'value2'})
