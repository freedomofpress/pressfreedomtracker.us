from datetime import date

from django.test import TestCase
from wagtail.wagtailcore.rich_text import RichText

from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentCategorizationFactory,
)
from common.tests.factories import CategoryPageFactory
from incident.utils.incident_filter import IncidentFilter


class TestFiltering(TestCase):
    def setUp(self):
        self.index = IncidentIndexPageFactory()

    def test_should_filter_by_date_range(self):
        target = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(
            search_text=None,
            categories=None,
            upper_date='2017-01-31',
            lower_date='2017-01-01',
        ).fetch()

        self.assertEqual({target}, set(incidents))

    def test_should_filter_by_date_range_unbounded_below(self):
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        incident2 = IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(
            search_text=None,
            categories=None,
            upper_date='2017-01-31',
            lower_date=None,
        ).fetch()

        self.assertEqual({incident2, incident1}, set(incidents))

    def test_should_filter_by_date_range_unbounded_above(self):
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        incident2 = IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(
            search_text=None,
            categories=None,
            upper_date=None,
            lower_date='2017-01-01',
        ).fetch()

        self.assertEqual({incident2, incident1}, set(incidents))

    def test_should_filter_by_search_text(self):
        incident1 = IncidentPageFactory(
            body__0__rich_text__value=RichText('eggplant'),
        )
        IncidentPageFactory(
            body__0__rich_text__value=RichText('science fiction'),
        )

        incidents = IncidentFilter(
            search_text='eggplant',
            categories=None,
            upper_date=None,
            lower_date=None,
        ).fetch()

        self.assertEqual({incident1}, set(incidents))

    def test_should_filter_by_category(self):
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        incident1 = IncidentPageFactory()
        not_relevant = IncidentPageFactory(title='Not relevant')

        ic1 = IncidentCategorizationFactory.create(
            category=category1,
            incident_page=incident1
        )
        ic1.save()
        ic2 = IncidentCategorizationFactory(
            category=category2,
            incident_page=not_relevant,
        )
        ic2.save()
        incidents = IncidentFilter(
            search_text=None,
            categories=str(category1.id),
            upper_date=None,
            lower_date=None,
        ).fetch()
        self.assertEqual({incident1}, set(incidents))

    def test_should_filter_by_any_category_given(self):
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        category3 = CategoryPageFactory()
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory(title='Not relevant')

        ic1 = IncidentCategorizationFactory.create(
            category=category1,
            incident_page=incident1
        )
        ic1.save()
        ic2 = IncidentCategorizationFactory(
            category=category2,
            incident_page=incident2,
        )
        ic2.save()
        ic3 = IncidentCategorizationFactory.create(
            category=category3,
            incident_page=incident1,
        )
        ic3.save()
        incidents = IncidentFilter(
            search_text=None,
            categories='{0},{1}'.format(str(category2.id), str(category3.id)),
            upper_date=None,
            lower_date=None,
        ).fetch()
        self.assertEqual({incident1, incident2}, set(incidents))

    def should_xyz(self):
        self.assertTrue(False)
