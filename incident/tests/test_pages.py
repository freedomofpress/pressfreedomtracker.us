import csv

import wagtail_factories
from wagtail.core.models import Site, Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (
    nested_form_data,
    streamfield,
    inline_formset,
    rich_text,
)
from django.test import TestCase, Client
from django.urls import reverse

from common.tests.factories import CategoryPageFactory, PersonPageFactory
from home.tests.factories import HomePageFactory
from incident.models.incident_page import IncidentPage
from incident.models.export import is_exportable, to_row
from .factories import IncidentIndexPageFactory, IncidentPageFactory


class TestPages(TestCase):
    """Incident Index Page """
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

    def test_get_index_should_succeed(self):
        """get index should succed."""
        response = self.client.get('/incidents/')
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_filters(self):
        """get index with filters should succeed."""
        response = self.client.get(
            '/incidents/?search=text&date_upper=2017-01-01&categories=1,2'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_malformed_filters(self):
        """get index should succeed with malformed filters."""
        response = self.client.get(
            '/incidents/?date_upper=aaa&date_lower=2011-54-39'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_blank_category_filters(self):
        """get index should succeed blank with a category filter."""
        response = self.client.get('/incidents/?categories=')
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_illegal_date_range(self):
        """get index should succeed with malformed filters."""
        response = self.client.get(
            '/incidents/?date_upper=2011-01-01&date_lower=2012-01-01'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_invalid_foreign_key(self):
        """get index should succeed with a noninteger foreign key reference."""
        response = self.client.get('/incidents/?state=NONINTEGER_VALUE')
        self.assertEqual(response.status_code, 200)


class TestExportPage(TestCase):
    """CSV Exports"""
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        cls.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=cls.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': cls.home_page,
            }
        )
        if not created:
            site.root_page = cls.home_page
            site.save()

        cls.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

    def test_export_should_succeed(self):
        """request should succeed."""
        response = self.client.get(
            '/incidents/export/'
        )
        self.assertEqual(response.status_code, 200)

    def test_export_should_include_headers(self):
        """ should include headers"""
        response = self.client.get(
            '/incidents/export/'
        )
        content_lines = list(response.streaming_content)
        expected_headers = [
            field.name for field in IncidentPage._meta.get_fields()
            if is_exportable(field)
        ]
        self.assertEqual(
            content_lines[0].decode('utf-8'),
            ','.join(expected_headers) + '\r\n',
        )

    def test_export_should_include_incidents_only_live_incidents(self):
        """should include only live incidents."""
        inc = IncidentPageFactory(parent=self.index, title='Live incident')
        IncidentPageFactory(
            parent=self.index,
            title='Unpublished incident',
            live=False
        )
        response = self.client.get(
            '/incidents/export/'
        )

        content_lines = list(response.streaming_content)
        reader = csv.reader(line.decode('utf-8') for line in content_lines)
        next(reader)  # skip the header row
        csv_line = next(reader)
        self.assertEqual(to_row(inc), csv_line)
        for line in content_lines:
            self.assertNotIn('Unpublished incident', line.decode('utf-8'))


class TestFeedsPage(WagtailPageTests):
    """RSS Feeds Page"""
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        cls.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=cls.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': cls.home_page,
            }
        )
        if not created:
            site.root_page = cls.home_page
            site.save()

        cls.category = CategoryPageFactory(parent=cls.home_page)
        cls.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')
        IncidentPageFactory(parent=cls.index)

    def test_feed_should_succeed(self):
        """request should succeed."""
        response = self.client.get(
            '/incidents/feed/'
        )
        self.assertEqual(response.status_code, 200)

    def test_feed_should_have_content(self):
        """request should succeed."""
        IncidentPageFactory(parent=self.index, title='The Incident')
        response = self.client.get(
            '/incidents/feed/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Incident')

    def test_feed_should_strip_unserializable_character(self):
        """request should succeed with unserializable chars."""
        IncidentPageFactory(
            parent=self.index,
            title='The Unserializable Character Incident',
            body=wagtail_factories.StreamFieldFactory({
                'rich_text': rich_text('<p>Lorem \x00 dolor sit amet</p>'),
                'raw_html': '<p>Lorem \x00 ipsum dolor sit amet</p>',
            })
        )
        response = self.client.get(
            '/incidents/feed/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Unserializable Character Incident")


class GetRelatedIncidentsTest(TestCase):
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page,
            slug='incidents',
        )
        self.category = CategoryPageFactory()

    def test_get_related_incidents__saved(self):
        IncidentPageFactory(parent=self.index)
        related_incident = IncidentPageFactory(parent=self.index)
        category_incident = IncidentPageFactory(parent=self.index, categories=[self.category])
        incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category],
            related_incidents=[related_incident],
        )

        related_incidents = incident.get_related_incidents()
        self.assertEqual(related_incidents, [related_incident, category_incident])

    def test_get_related_incidents__unsaved(self):
        IncidentPageFactory(parent=self.index)
        related_incident = IncidentPageFactory(parent=self.index)
        category_incident = IncidentPageFactory(parent=self.index, categories=[self.category])
        incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category]
        )

        incident.related_incidents = [related_incident]

        related_incidents = incident.get_related_incidents()
        self.assertEqual(related_incidents, [related_incident, category_incident])

    def test_get_related_incidents__include_related_once_only(self):
        # Related incidents should only be included once, for being related
        # and not a second time for being in the same category.
        IncidentPageFactory(parent=self.index)
        related_incident = IncidentPageFactory(parent=self.index, categories=[self.category])
        incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category],
            related_incidents=[related_incident],
        )

        related_incidents = incident.get_related_incidents()
        self.assertEqual(related_incidents, [related_incident])


class IncidentPageStatisticsTagsTestCase(WagtailPageTests):
    @classmethod
    def setUpTestData(cls):
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        cls.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=cls.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': cls.home_page,
            }
        )
        if not created:
            site.root_page = cls.home_page
            site.save()

        cls.site = site
        cls.category = CategoryPageFactory(parent=cls.home_page)
        cls.author = PersonPageFactory(parent=cls.home_page)
        cls.index_page = IncidentIndexPageFactory(
            parent=cls.home_page,
        )

    def test_can_preview_incident_page(self):
        stats_tag = '{{% num_incidents categories="{}" %}}'.format(self.category.pk)
        incident_page = IncidentPageFactory(parent=self.category)

        preview_url = reverse('wagtailadmin_pages:preview_on_edit', args=(incident_page.pk,))
        response = self.client.post(
            preview_url,
            nested_form_data({
                'title': 'The Incident',
                'slug': 'the-incident',
                'date': '2019-04-16',
                'body': streamfield([
                    ('raw_html', '<p>Lorem ipsum dolor sit amet</p>'),
                    ('rich_text', rich_text('<p>Lorem {} dolor sit amet</p>'.format(stats_tag))),
                ]),
                'state': 'null',
                'targets': 'null',
                'tags': 'null',
                'current_charges': 'null',
                'dropped_charges': 'null',
                'venue': 'null',
                'target_nationality': 'null',
                'targets_whose_communications_were_obtained': 'null',
                'politicians_or_public_figures_involved': 'null',
                'related_incidents': 'null',
                'updates': inline_formset([]),
                'links': inline_formset([]),
                'categories': inline_formset([
                    {'category': str(self.category.pk)},
                ]),
                'authors': inline_formset([
                    {'author': str(self.author.pk)},
                ]),
                'equipment_seized': inline_formset([]),
                'equipment_broken': inline_formset([]),
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {'is_valid': True})
        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], incident_page)

    def test_can_create_incident_page(self):
        stats_tag = '{{% num_incidents categories="{}" %}}'.format(self.category.pk)
        self.assertCanCreate(self.index_page, IncidentPage, nested_form_data({
            'title': 'The Incident',
            'slug': 'the-incident',
            'date': '2019-04-16',
            'body': streamfield([
                ('raw_html', '<p>Lorem ipsum dolor sit amet</p>'),
                ('rich_text', rich_text('<p>Lorem {} dolor sit amet</p>'.format(stats_tag))),
            ]),
            'state': 'null',
            'targets': 'null',
            'tags': 'null',
            'current_charges': 'null',
            'dropped_charges': 'null',
            'venue': 'null',
            'target_nationality': 'null',
            'targets_whose_communications_were_obtained': 'null',
            'politicians_or_public_figures_involved': 'null',
            'related_incidents': 'null',
            'updates': inline_formset([]),
            'links': inline_formset([]),
            'categories': inline_formset([
                {'category': str(self.category.pk)},
            ]),
            'authors': inline_formset([
                {'author': str(self.author.pk)},
            ]),
            'equipment_seized': inline_formset([]),
            'equipment_broken': inline_formset([]),
        }))

        incident_page = IncidentPage.objects.get(slug='the-incident')
        response = self.client.get(incident_page.url)
        self.assertEqual(response.status_code, 200)
