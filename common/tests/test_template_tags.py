import hashlib
from unittest import mock

from django.http import QueryDict
from django.test import TestCase, RequestFactory

from common.templatetags.common_tags import (
    lookup,
    add_as_string,
    richtext_aside,
    query_transform,
    get_absolute_url,
)


class TestTemplateTags(TestCase):
    def test_lookup(self):
        obj = {
            'some_key': 'some_value'
        }

        self.assertEqual(lookup(obj, 'some_key'), 'some_value')

    def test_lookup_not_found_returns_empty_string(self):
        obj = {
            'some_key': 'some_value'
        }

        self.assertEqual(lookup(obj, 'some_other_key'), '')

    def test_add_as_string(self):
        part_string = 'A value with a number at the end: '
        whole_string = 'A value with a number at the end: 2'

        self.assertEqual(add_as_string(part_string, 2), whole_string)

    def test_add_as_string_multiple_coercion_errors_returns_empty_string(self):
        part_string = 'A value with a number at the end: '
        bad_object = mock.MagicMock()
        bad_object.__str__.side_effect = ValueError
        bad_object.__radd__.side_effect = ValueError

        self.assertEqual(add_as_string(part_string, bad_object), '')

    def test_add_as_string_single_coercion_error_defaults_to_addition(self):
        part_string = 'A value with a number at the end: '
        bad_object = mock.MagicMock()
        bad_object.__str__.side_effect = TypeError
        bad_object.__radd__.return_value = 'I was added to something'

        self.assertEqual(add_as_string(part_string, bad_object), 'I was added to something')

    def test_richtext_aside(self):
        paragraph_aside = '<p data-block-key="89kgh">This is paragraph with <b>bold text</b></p>'
        paragraph_aside_with_span = '<p data-block-key="89kgh"><span>This is paragraph with <b>bold text</b></span></p>'

        heading_aside = '<h3 data-block-key="89agh">This is a heading</h3>'
        heading_aside_with_span = '<h3 data-block-key="89agh"><span>This is a heading</span></h3>'

        self.assertEqual(richtext_aside(paragraph_aside), paragraph_aside_with_span)
        self.assertEqual(richtext_aside(heading_aside), heading_aside_with_span)

    @mock.patch('django.core.cache.cache.get')
    def test_cache_usage_in_richtext_aside(self, mock_django_cache_get):
        paragraph_aside = '<p data-block-key="89kgh">This is paragraph with <b>bold text</b></p>'
        heading_aside = '<h3 data-block-key="89agh">This is a heading</h3>'
        paragraph_aside_hash = hashlib.md5(
            paragraph_aside.encode('UTF-8'),
            usedforsecurity=False,
        ).hexdigest()
        paragraph_aside_cache_key = f"aside_html_cache_{paragraph_aside_hash}"

        richtext_aside(paragraph_aside)
        self.assertFalse(mock_django_cache_get.called)

        # Testing that calling with the different HTML string doesn't call cache.get
        richtext_aside(heading_aside)
        self.assertFalse(mock_django_cache_get.called)

        # Testing that calling with the same HTML string calls the cache.get
        richtext_aside(paragraph_aside)
        self.assertTrue(mock_django_cache_get.called)
        self.assertEqual(mock_django_cache_get.call_count, 1)
        mock_django_cache_get.assert_called_once_with(paragraph_aside_cache_key)

    def test_query_transform(self):
        request = RequestFactory().get('/?page=1&sort=title')
        result = query_transform(request, page=2)

        # Parse result using Django's QueryDict for ease of assertion
        qd = QueryDict(result)
        self.assertEqual(qd['page'], '2')
        self.assertEqual(qd['sort'], 'title')

    def test_query_transform_removes_keys_set_to_none(self):
        request = RequestFactory().get('/?page=1&sort=title')
        result = query_transform(request, sort=None)

        # Parse result using Django's QueryDict for ease of assertion
        qd = QueryDict(result)
        self.assertEqual(qd['page'], '1')
        self.assertTrue('sort' not in qd)

    def test_query_transform_ignores_unknown_keys_set_to_none(self):
        request = RequestFactory().get('/?page=1&sort=title')
        result = query_transform(request, tree=None)

        # Parse result using Django's QueryDict for ease of assertion
        qd = QueryDict(result)
        self.assertEqual(qd['page'], '1')
        self.assertEqual(qd['sort'], 'title')

    def test_get_absolute_url(self):
        request = RequestFactory().get('/')
        context = {'request': request}

        result = get_absolute_url(context, 'sitemap')

        self.assertEqual(result, 'http://testserver/sitemap.xml')
