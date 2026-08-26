from django.core.management import call_command
from django.test import TestCase

from common.models import CommonTag
from incident.tests.factories import IncidentPageFactory

from .factories import CommonTagFactory


class TestPruneUnusedTags(TestCase):
    def test_deletes_unused_tags(self):
        _unused_tag, used_tag = CommonTagFactory.create_batch(2)
        incident = IncidentPageFactory()
        used_tag.tagged_items.add(incident)

        call_command("prune_unused_tags")
        self.assertEqual(list(CommonTag.objects.all()), [used_tag])
