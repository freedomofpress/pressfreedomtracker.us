import csv
import json
import unittest
from datetime import timedelta, date
from urllib import parse

import wagtail_factories
from wagtail.core.models import Site, Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (
    nested_form_data,
    streamfield,
    inline_formset,
    rich_text,
)
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from common.models import IncidentFilterSettings, GeneralIncidentFilter, SearchSettings
from common.tests.factories import (
    SimplePageFactory,
    CategoryPageFactory,
    PersonPageFactory,
    CommonTagFactory,
    CustomImageFactory,
)
from geonames.models import Country, Region, GeoName
from home.tests.factories import HomePageFactory
from incident.models.incident_page import IncidentPage
from incident.models.topic_page import TopicPage
from incident.models.export import is_exportable, to_row
from .factories import (
    IncidentIndexPageFactory,
    IncidentPageFactory,
    IncidentLinkFactory,
    IncidentUpdateFactory,
    TopicPageFactory,
    StateFactory,
    InstitutionFactory,
    TargetedJournalistFactory,
)


class TestPages(TestCase):
    """Incident Index Page """
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

        incident_filter_settings = IncidentFilterSettings.for_site(site)
        cls.search_settings = SearchSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=incident_filter_settings,
            incident_filter='state',
        )
        cls.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')
        cls.incident = IncidentPageFactory(parent=cls.index, slug='one')

    def setUp(self):
        self.client = Client()

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

    def test_get_index_should_succeed_with_noninteger_page_number(self):
        """get index should succeed with a noninteger foreign key reference."""
        response = self.client.get('/incidents/?page=abc')
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_noninteger_endpage_number(self):
        """get index should succeed with a noninteger foreign key reference."""
        response = self.client.get('/incidents/?endpage=abc')
        self.assertEqual(response.status_code, 200)

    def test_get_incident_page_should_succeed(self):
        response = self.client.get('/incidents/one/')
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_not_include_learn_more_link(self):
        response = self.client.get(self.index.get_url())
        self.assertNotContains(response, 'Learn more')

    def test_get_index_should_include_learn_more_link_if_page_specified(self):
        url = self.index.get_url()
        self.search_settings.learn_more_page = SimplePageFactory(parent=self.home_page)
        self.search_settings.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestIncidentIndexPageContext(TestCase):
    def setUp(self):
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        self.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=self.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': self.home_page,
            }
        )
        if not created:
            site.root_page = self.home_page
            site.save()

        self.settings = IncidentFilterSettings.for_site(site)
        self.search_settings = SearchSettings.for_site(site)
        self.site = site
        self.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

    def test_includes_export_path(self):
        request = RequestFactory().get('/')
        context = self.index.get_context(request)
        self.assertEqual(
            context['export_path'],
            self.index.get_url() + self.index.reverse_subpage('export_view')
        )

    def test_includes_total_incident_count(self):
        IncidentPageFactory.create_batch(3, parent=self.index)
        request = RequestFactory().get('/')
        context = self.index.get_context(request)
        self.assertEqual(context['all_incident_count'], 3)

    def test_includes_filtered_export_path(self):
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=self.settings,
            incident_filter='city',
        )

        request = RequestFactory().get('/?city=Albuquerque')
        context = self.index.get_context(request)
        expected_path = (
            self.index.get_url() +
            self.index.reverse_subpage('export_view') +
            '?city=Albuquerque'
        )
        self.assertEqual(context['filtered_export_path'], expected_path)

    def test_includes_search_value(self):
        search_query = 'delicious treats'
        request = RequestFactory().get(
            '/?' + parse.urlencode({'search': search_query})
        )
        context = self.index.get_context(request)
        self.assertEqual(context['search_value'], search_query)

    def test_does_not_include_learn_more_path_if_page_not_in_settings(self):
        self.search_settings.learn_more_page = None
        self.search_settings.save()
        request = RequestFactory().get('/')
        context = self.index.get_context(request)
        self.assertNotIn('learn_more_path', context)

    def test_includes_learn_more_path_if_page_in_settings(self):
        self.search_settings.learn_more_page = self.home_page
        self.search_settings.save()
        request = RequestFactory().get('/')
        context = self.index.get_context(request)
        self.assertEqual(
            context['learn_more_path'],
            self.home_page.get_url(),
        )


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
        # Last elem in these lists is GenericRelatedObjectManager which will have different
        # IDs
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

    def test_related_incidents_sorted_by_date(self):
        IncidentPageFactory(parent=self.index)

        related_incident_old = IncidentPageFactory(parent=self.index, date='2016-01-01')
        related_incident_new = IncidentPageFactory(parent=self.index, date='2020-01-01')
        related_incident_recent = IncidentPageFactory(parent=self.index, date='2019-01-01')

        incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category],
            related_incidents=[
                related_incident_old,
                related_incident_new,
                related_incident_recent,
            ],
        )

        related_incidents = incident.get_related_incidents()
        self.assertEqual(
            related_incidents,
            [related_incident_new, related_incident_recent, related_incident_old],
        )

    def test_get_related_incidents__saved(self):
        IncidentPageFactory(parent=self.index)
        tag = CommonTagFactory()
        related_incident = IncidentPageFactory(parent=self.index)
        tagged_incident = IncidentPageFactory(parent=self.index, categories=[self.category], tags=[tag])
        incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category],
            related_incidents=[related_incident],
            tags=[tag],
        )

        related_incidents = incident.get_related_incidents()
        self.assertEqual(related_incidents, [related_incident, tagged_incident])

    def test_get_related_incidents__unsaved(self):
        IncidentPageFactory(parent=self.index)
        tag = CommonTagFactory()
        related_incident = IncidentPageFactory(parent=self.index)
        tagged_incident = IncidentPageFactory(parent=self.index, categories=[self.category], tags=[tag])
        incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category],
            tags=[tag],
        )

        incident.related_incidents = [related_incident]

        related_incidents = incident.get_related_incidents()
        self.assertEqual(related_incidents, [related_incident, tagged_incident])

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

    def test_get_related_incidents__using_tags(self):
        tag1 = CommonTagFactory()
        tag2 = CommonTagFactory()
        tag3 = CommonTagFactory()
        tag4 = CommonTagFactory()
        state = StateFactory()
        subject = IncidentPageFactory(
            parent=self.index,
            tags=[tag1, tag2, tag3],
            categories=[self.category],
            state=state,
        )

        closely_related = IncidentPageFactory(
            title='Closely',
            state=state,
            parent=self.index,
            tags=[tag1, tag2, tag3],
            categories=[self.category],
        )
        somewhat_related = IncidentPageFactory(
            title='Somewhat',
            state=state,
            parent=self.index,
            tags=[tag1, tag3],
            categories=[self.category],
        )
        slightly_related = IncidentPageFactory(
            title='Slightly',
            state=state,
            parent=self.index,
            tags=[tag2, tag4],
            categories=[self.category]
        )
        IncidentPageFactory(
            title='Not related',
            state=None,
            parent=self.index,
            tags=[tag4],
            categories=[self.category],
        )

        related_incidents = subject.get_related_incidents()

        self.assertEqual(
            related_incidents,
            [closely_related, somewhat_related, slightly_related]
        )

    def test_get_related_incidents__ordered_by_descending_date(self):
        tag1 = CommonTagFactory()
        tag2 = CommonTagFactory()
        tag3 = CommonTagFactory()

        subject = IncidentPageFactory(parent=self.index, tags=[tag1, tag2, tag3], categories=[self.category])

        closely_related_old = IncidentPageFactory(
            parent=self.index,
            tags=[tag1, tag2, tag3],
            state=None,
            categories=[self.category],
            date='2016-01-01',
        )
        closely_related_new = IncidentPageFactory(
            parent=self.index,
            tags=[tag1, tag2, tag3],
            state=None,
            categories=[self.category],
            date='2020-01-01',
        )
        closely_related_recent = IncidentPageFactory(
            parent=self.index,
            tags=[tag1, tag2, tag3],
            state=None,
            categories=[self.category],
            date='2019-01-01',
        )
        related_incidents = subject.get_related_incidents()

        self.assertEqual(
            related_incidents,
            [closely_related_new, closely_related_recent, closely_related_old]
        )

    def test_get_related_incidents__using_location(self):
        tag1 = CommonTagFactory()
        tag2 = CommonTagFactory()
        tag3 = CommonTagFactory()
        tag4 = CommonTagFactory()
        state = StateFactory()
        other_state = StateFactory()
        subject = IncidentPageFactory(
            parent=self.index,
            tags=[tag1, tag2, tag3],
            categories=[self.category],
            city='Albuquerque',
            state=state,
        )
        close = IncidentPageFactory(
            title='Close',
            parent=self.index,
            tags=[tag2],
            categories=[self.category],
            city='Albuquerque',
            state=state,
        )
        nearby = IncidentPageFactory(
            title='Nearby',
            parent=self.index,
            tags=[tag3],
            categories=[self.category],
            city='Santa Fe',
            state=state,
        )
        far = IncidentPageFactory(
            title='Far',
            parent=self.index,
            tags=[tag1],
            categories=[self.category],
            city='Denver',
            state=other_state,
        )
        nearby_no_tag_overlap = IncidentPageFactory(
            title='Nearby, no tag overlap',
            parent=self.index,
            tags=[tag4],
            categories=[self.category],
            city='Santa Fe',
            state=state,
        )
        IncidentPageFactory(
            title='No relation',
            parent=self.index,
            tags=[tag4],
            categories=[self.category],
            city='Denver',
            state=other_state,
        )
        related_incidents = subject.get_related_incidents()

        self.assertEqual(related_incidents, [close, nearby, far, nearby_no_tag_overlap])


class RecentlyUpdatedMethod(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get()
        cls.index = IncidentIndexPageFactory(
            parent=site.root_page,
            slug='incidents',
        )

        cls.inc1, cls.inc2, cls.inc3 = IncidentPageFactory.create_batch(
            3,
            parent=cls.index,
        )
        IncidentUpdateFactory(
            page=cls.inc1,
            date=timezone.now() - timedelta(days=30),
        )
        IncidentUpdateFactory(
            page=cls.inc2,
            date=timezone.now() - timedelta(days=3),
        )
        IncidentUpdateFactory(
            page=cls.inc3,
            date=timezone.now(),
        )

    def test_knows_if_an_incident_was_updated_in_the_past_week(self):
        self.assertFalse(self.inc1.recently_updated())
        self.assertTrue(self.inc2.recently_updated())
        self.assertTrue(self.inc3.recently_updated())

    def test_runs_no_queries_if_information_cached(self):
        incidents = IncidentPage.objects.with_most_recent_update().all()
        for incident in incidents:
            with self.assertNumQueries(0):
                incident.recently_updated()

    def test_annotates_the_date_of_the_latest_update(self):
        update1 = IncidentUpdateFactory(
            page=self.inc1,
            date=timezone.now() - timedelta(days=10),
        )
        IncidentUpdateFactory(
            page=self.inc1,
            date=timezone.now() - timedelta(days=15),
        )
        incident = IncidentPage.objects.with_most_recent_update() \
            .get(pk=self.inc1.pk)

        self.assertEqual(incident.latest_update, update1.date)


class GetIncidentUpdatesTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page,
            slug='incidents',
        )

    def test_get_incident_updates_sorted_by_asc_date(self):
        incident = IncidentPageFactory(parent=self.index)
        incident_update1 = IncidentUpdateFactory(
            page=incident,
            date=timezone.now() - timedelta(days=30),
        )
        incident_update2 = IncidentUpdateFactory(
            page=incident,
            date=timezone.now() - timedelta(days=3),
        )
        incident_update3 = IncidentUpdateFactory(
            page=incident,
            date=timezone.now() - timedelta(days=300),
        )

        incident_updates = incident.get_updates_by_asc_date()

        self.assertEqual(
            list(incident_updates),
            [incident_update3, incident_update1, incident_update2]
        )


@unittest.skip("Skipping till templates have been added")
class IncidentPageStatisticsTagsTestCase(WagtailPageTests):
    def setUp(self):
        super().setUp()
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        self.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=self.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': self.home_page,
            }
        )
        if not created:
            site.root_page = self.home_page
            site.save()

        self.site = site
        self.category = CategoryPageFactory(parent=self.home_page)
        self.author = PersonPageFactory(parent=self.home_page)
        self.index_page = IncidentIndexPageFactory(
            parent=self.home_page,
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
                'targeted_institutions': 'null',
                'targeted_journalists': inline_formset([]),
                'tags': 'null',
                'current_charges': 'null',
                'dropped_charges': 'null',
                'arresting_authority': 'null',
                'venue': 'null',
                'target_nationality': 'null',
                'targets_whose_communications_were_obtained': 'null',
                'workers_whose_communications_were_obtained': 'null',
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
            'targeted_institutions': 'null',
            'targeted_journalists': inline_formset([]),
            'tags': 'null',
            'current_charges': 'null',
            'dropped_charges': 'null',
            'arresting_authority': 'null',
            'venue': 'null',
            'target_nationality': 'null',
            'targets_whose_communications_were_obtained': 'null',
            'workers_whose_communications_were_obtained': 'null',
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


class TestTopicPage(WagtailPageTests):
    def setUp(self):
        self.login()
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        self.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=self.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': self.home_page,
            }
        )
        if not created:
            site.root_page = self.home_page
            site.save()

        self.site = site
        self.category = CategoryPageFactory(parent=self.home_page)
        self.tag = CommonTagFactory()
        self.index_page = IncidentIndexPageFactory(
            parent=self.home_page,
        )

    @unittest.skip("Skipping till templates have been added")
    def test_can_create_topic_page(self):
        stats_tag = '{{% num_incidents categories="{}" %}}'.format(self.category.pk)

        form_data = nested_form_data({
            'title': 'Vampires',
            'slug': 'vampires',
            'superheading': 'The Children of the Night',
            'description': rich_text('<p>Creatures feeding on vital essence.</p>'),
            'text_align': 'bottom-center',
            'text_color': 'black',
            'photo_caption': rich_text('<p>Possibly some fangs.</p>'),
            'photo_credit': 'Professor Abraham Van Helsing',
            'photo_credit_link': 'https://example.com',
            'content': streamfield([
                ('heading_2', nested_form_data({'content': 'What is a Vampire?'})),
                ('raw_html', '<figure><img src="/media/example.jpg"><figcaption>A vampire at sunset</figcaption></figure>'),
                ('rich_text', rich_text('<p><i>Lorem ipsum</i></p>')),
            ]),
            'sidebar': streamfield([
                ('heading_2', nested_form_data({'content': 'Vampire Sightings 2020'})),
                ('rich_text', rich_text('<p><i>Lorem ipsum</i></p>')),
                ('button', nested_form_data({
                    'text': 'Donate blood',
                    'url': 'https://example.com',
                })),
                ('stat_table', streamfield([
                    ('value', nested_form_data({'header': 'Garlic Supplies', 'value': '6 heads'})),
                    ('value', nested_form_data({'header': 'Recent attacks', 'value': stats_tag})),
                ])),
            ]),
            'incident_tag': json.dumps({'title': self.tag.title, 'pk': self.tag.pk}),
            'incident_index_page': self.index_page.pk,
            'incidents_per_module': 4,
            'layout': 'by_category',
        })

        self.assertCanCreate(self.home_page, TopicPage, form_data)
        topic_page = TopicPage.objects.get(slug='vampires')
        response = self.client.get(topic_page.url)
        self.assertEqual(response.status_code, 200)

    @unittest.skip("Skipping till templates have been added")
    def test_can_preview_topic_page(self):
        topic_page = TopicPageFactory(
            parent=self.home_page,
            incident_index_page=self.index_page
        )
        preview_url = reverse('wagtailadmin_pages:preview_on_edit', args=(topic_page.pk,))

        stats_tag = '{{% num_incidents categories="{}" %}}'.format(self.category.pk)
        form_data = nested_form_data({
            'title': 'Vampires',
            'slug': 'vampires',
            'superheading': 'The Children of the Night',
            'description': rich_text('<p>Creatures feeding on vital essence.</p>'),
            'text_align': 'bottom-center',
            'text_color': 'black',
            'photo_caption': rich_text('<p>Possibly some fangs.</p>'),
            'photo_credit': 'Professor Abraham Van Helsing',
            'photo_credit_link': 'https://example.com',
            'content': streamfield([
                ('heading_2', nested_form_data({'content': 'What is a Vampire?'})),
                ('raw_html', '<figure><img src="/media/example.jpg"><figcaption>A vampire at sunset</figcaption></figure>'),
                ('rich_text', rich_text('<p><i>Lorem ipsum</i></p>')),
            ]),
            'sidebar': streamfield([
                ('heading_2', nested_form_data({'content': 'Vampire Sightings 2020'})),
                ('rich_text', rich_text('<p><i>Lorem ipsum</i></p>')),
                ('button', nested_form_data({
                    'text': 'Donate blood',
                    'url': 'https://example.com',
                })),
                ('stat_table', streamfield([
                    ('value', nested_form_data({'header': 'Garlic Supplies', 'value': '6 heads'})),
                    ('value', nested_form_data({'header': 'Recent attacks', 'value': stats_tag})),
                ])),
            ]),
            'incident_tag': json.dumps({'title': self.tag.title, 'pk': self.tag.pk}),
            'incident_index_page': self.index_page.pk,
            'incidents_per_module': 4,
            'layout': 'by_category',
        })

        response = self.client.post(
            preview_url,
            form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {'is_valid': True})
        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], topic_page)

    def test_sorts_incidents_by_incident_date_descending(self):
        topic_page = TopicPageFactory(
            parent=self.home_page,
            incident_index_page=self.index_page
        )
        incident1 = IncidentPageFactory(date=date(2020, 1, 2), tags=[topic_page.incident_tag])
        incident2 = IncidentPageFactory(date=date(2020, 1, 3), tags=[topic_page.incident_tag])
        incident3 = IncidentPageFactory(date=date(2020, 1, 1), tags=[topic_page.incident_tag])

        request = RequestFactory().get('/')

        self.assertEqual(
            list(topic_page.get_context(request)['entries_page']),
            [incident2, incident1, incident3]
        )

    def test_filters_incidents_by_date_range(self):
        topic_page = TopicPageFactory(
            parent=self.home_page,
            incident_index_page=self.index_page,
            start_date='2021-01-15',
            end_date='2021-02-15',
        )
        IncidentPageFactory(date=date(2021, 1, 2), tags=[topic_page.incident_tag])
        incident1 = IncidentPageFactory(date=date(2021, 1, 2), exact_date_unknown=True, tags=[topic_page.incident_tag])
        incident2 = IncidentPageFactory(date=date(2021, 2, 3), tags=[topic_page.incident_tag])
        IncidentPageFactory(date=date(2021, 3, 4), tags=[topic_page.incident_tag])

        request = RequestFactory().get('/')

        self.assertEqual(
            list(topic_page.get_context(request)['entries_page']),
            [incident2, incident1]
        )


class IncidentPageQueriesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

        image = CustomImageFactory.create(
            file__width=800,
            file__height=600,
            file__color='red',
        )

        author1, author2, author3 = PersonPageFactory.create_batch(3, parent=root_page)
        cls.cat1, cls.cat2, cls.cat3 = CategoryPageFactory.create_batch(3, parent=root_page)

        incidents = IncidentPageFactory.create_batch(
            50,
            parent=cls.incident_index,
            authors=[author1, author2],
            categories=[cls.cat1, cls.cat2],
            equipment_search=True,
            equipment_damage=True,
            arrest=True,
            border_stop=True,
            physical_attack=True,
            leak_case=True,
            workers_whose_communications_were_obtained=2,
            subpoena=True,
            prior_restraint=True,
            target_nationality=2,
            journalist_targets=2,
            institution_targets=2,
            teaser_image=image,
            current_charges=2,
            dropped_charges=2,
            politicians_or_public_figures_involved=3,
        )
        for incident in incidents:
            tags = CommonTagFactory.create_batch(3)
            incident.tags = tags
            incident.save()
            IncidentUpdateFactory.create_batch(2, page=incident)
            IncidentLinkFactory.create_batch(3, page=incident)

            # Pre-generate renditions to avoid INSERT queries that we
            # don't want to count.
            incident.teaser_image.get_rendition('fill-1330x880')

    def test_api_selects_and_prefetches(self):
        # 1 base query, plus 20 prefetches.
        with self.assertNumQueries(21):
            list(IncidentPage.objects.with_public_associations())


class IncidentPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

        cls.site = site

    def test_computes_unique_date(self):
        incident1 = IncidentPage(
            date=date(2020, 6, 16),
            title='Test Incident 1',
        )
        incident2 = IncidentPage(
            date=date(2020, 6, 16),
            title='Test Incident 2',
        )
        self.incident_index.add_child(instance=incident1)
        self.incident_index.add_child(instance=incident2)

        UNIQUE_DATE_FORMAT = r'\d{4}-\d{2}-\d{2}-[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'

        self.assertRegex(
            incident1.unique_date,
            UNIQUE_DATE_FORMAT
        )

        self.assertRegex(
            incident2.unique_date,
            UNIQUE_DATE_FORMAT
        )

        self.assertNotEqual(
            incident1.unique_date,
            incident2.unique_date
        )

    def test_looks_up_latitude_longitude_from_city_and_state(self):
        incident_index = IncidentIndexPageFactory.build(title='A title')
        self.site.root_page.add_child(instance=incident_index)

        united_states = Country.objects.create(
            isocode=1,
            iso='US',
            iso3='USA',
            fips='US',
            name='United States',
            capital='Washington',
            geonameid=1,
        )

        Region.objects.create(
            isocode=united_states,
            regcode='AK2',
            name='Alaska 2',
            geonameid=1,
        )
        state = StateFactory(
            name='Alaska 2',
            abbreviation='AK2',
        )

        geoname = GeoName.objects.create(
            geonameid=1,
            name='City X',
            latitude=1.0,
            longitude=2.0,
            isocode=united_states,
            regcode='AK2',
        )
        incident = IncidentPage(
            date=date.today(),
            title='Incident with Geodata',
            city=geoname.name,
            state=state,
        )
        incident_index.add_child(instance=incident)
        self.assertEqual(incident.longitude, geoname.longitude)
        self.assertEqual(incident.latitude, geoname.latitude)

    def test_gets_unified_list_of_all_targets(self):
        inst = InstitutionFactory()
        inc = IncidentPageFactory(
            parent=self.incident_index,
        )
        inc.targeted_institutions = [inst]
        inc.save()
        tj1 = TargetedJournalistFactory(
            journalist__title='Alex Aardvark',
            institution=None,
            incident=inc,
        )
        tj2 = TargetedJournalistFactory(
            journalist__title='Benny Bird',
            incident=inc,
        )
        self.assertEqual(
            inc.get_all_targets_for_display,
            f'{tj1.journalist.title}, {tj2.journalist.title} ({tj2.institution.title}), {inst.title}'
        )
