from itertools import combinations, chain

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import CategoryPage
from incident.models import IncidentIndexPage
from incident.tests.factories import MultimediaIncidentPageFactory


def lookup_category(key):
    return CategoryPage.objects.get(slug=key)


def three_combinations(iterable):
    "generate all combinations of 1, 2, or 3 elements of an iterable"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in [1, 2, 3])


def generate_variations():
    """Generate a list of many possible combinations of factory parameters

    Iterates over all Traits declared on IncidentPageFactory and
    returns a list of dicts suitable for keyword arguments, e.g.:
    [{'arrest': True}, {'arrest': True, 'border_stop': True}, ...]

    """
    for variation in three_combinations(MultimediaIncidentPageFactory._meta.parameters.keys()):
        yield {k: True for k in variation}


class Command(BaseCommand):
    help = 'Create randomized incidents for testing'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating incidents')
        index = IncidentIndexPage.objects.first()

        for kwargs in generate_variations():
            for i in range(2):
                MultimediaIncidentPageFactory(
                    parent=index,
                    categories=[lookup_category(key) for key in kwargs.keys()],
                    **kwargs,
                )
