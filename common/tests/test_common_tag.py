from django.core.exceptions import ValidationError
from django.test import TestCase

from common.models import CommonTag
from .factories import CommonTagFactory
from incident.tests.factories import IncidentPageFactory


class TestUnusedTags(TestCase):
    def test_finds_unused_tags(self):
        """Should be able to query for tags that are not on any incidents."""
        unused_tag, used_tag = CommonTagFactory.create_batch(2)
        incident = IncidentPageFactory()
        used_tag.tagged_items.add(incident)

        self.assertEqual(list(CommonTag.objects.unused()), [unused_tag])

    def test_tags_incident_count_property(self):
        """Should be able to get the correct incident count from the property."""
        tag = CommonTagFactory()
        incident = IncidentPageFactory()
        tag.tagged_items.add(incident)

        self.assertEqual(tag.incident_count, 1)

    def test_validation_autocomplete_tag_creation(self):
        with self.assertRaises(ValidationError):
            CommonTag.autocomplete_create('hello,world')
