import datetime

from django.test import TestCase

from incident.tests.factories import IncidentPageFactory
from statistics.templatetags.statistics_tags import (
    incidents_in_year_range_by_month,
    num_incidents,
)


class StatisticsTestCase(TestCase):
    def assert_is_map(self, obj):
        """Assert that an object is a statistics map object

        This function will raise an AssertionError if the given object
        is not a "statistical map", i.e. a list of 2-tuples or an empty
        list.

        """
        self.assertIsInstance(obj, list)
        for item in obj:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)


class TestNumIncidents(StatisticsTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.incident = IncidentPageFactory(date=datetime.date(2017, 1, 1))
        cls.old_incident = IncidentPageFactory(date=datetime.date(2016, 1, 1))

    def test_should_be_type_number(self):
        self.assertIsInstance(num_incidents(2017), int)

    def test_should_find_incidents_in_2017(self):
        self.assertEqual(num_incidents(2017), 1)

    def test_should_find_incidents_in_2016(self):
        self.assertEqual(num_incidents(2016), 1)


class TestIncidentsInYearRangeByMonth(StatisticsTestCase):
    @classmethod
    def setUpTestData(cls):
        IncidentPageFactory(date=datetime.date(2017, 1, 1))
        IncidentPageFactory(date=datetime.date(2017, 2, 1))
        IncidentPageFactory(date=datetime.date(2016, 1, 1))
        IncidentPageFactory(date=datetime.date(2015, 1, 1))

    def test_should_be_type_map(self):
        incidents = incidents_in_year_range_by_month(2016, 2017)
        self.assert_is_map(incidents)
