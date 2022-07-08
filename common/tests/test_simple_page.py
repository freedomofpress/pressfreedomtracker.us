import unittest

from django.urls import reverse
from wagtail.core.models import Site, Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (
    nested_form_data,
    streamfield,
    rich_text,
)

from common.models import SimplePage
from common.tests.factories import CategoryPageFactory, SimplePageFactory
from home.tests.factories import HomePageFactory


class SimplePageStatisticsTagsTestCase(WagtailPageTests):
    def setUp(self):
        super(SimplePageStatisticsTagsTestCase, self).setUp()
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

        stats_tag = '{{% num_incidents categories="{}" %}}'.format(self.category.pk)
        self.page_data = {
            'title': 'Page 1',
            'slug': 'page-1',
            'body': streamfield([
                (
                    'text',
                    nested_form_data({
                        'text': rich_text('<p>Lorem {} dolor sit amet</p>'.format(stats_tag)),
                        'background_color': 'gamboge',
                        'text_align': 'left',
                        'font_size': 'normal',
                        'font_family': 'serif',
                    })
                )
            ]),
            'sidebar_content': streamfield([
                ('rich_text', rich_text('Lorem ipsum')),
            ])
        }

    def test_can_create_simple_page(self):
        self.assertCanCreate(
            self.home_page,
            SimplePage,
            nested_form_data(self.page_data),
        )

        incident_page = SimplePage.objects.get(slug='page-1')
        response = self.client.get(incident_page.url)
        self.assertEqual(response.status_code, 200)

    def test_can_preview_simple_page(self):
        simple_page = SimplePageFactory(parent=self.home_page)

        preview_url = reverse('wagtailadmin_pages:preview_on_edit', args=(simple_page.pk,))

        response = self.client.post(
            preview_url,
            nested_form_data(self.page_data)
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {'is_valid': True})

        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], simple_page)
