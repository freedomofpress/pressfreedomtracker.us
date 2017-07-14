import random

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import CategoryPage
from incident.models import (
    IncidentIndexPage,
    IncidentCategorization,
)
from incident.tests.factories import IncidentPageFactory


def lookup_category(name):
    return CategoryPage.objects.get(title=name)


class Command(BaseCommand):
    help = 'Create randomized incidents for testing'

    @transaction.atomic
    def handle(self, *args, **options):
        index = IncidentIndexPage.objects.first()

        incident_kinds = [
            ('arrest', True),
            ('equipment_seizure', True),
            ('border_stop', True),
            ('physical_assault', True),
            ('leak_prosecution', True),
            ('subpoena', True),
            ('legal_order_for_records', True),
            ('prior_restraint', True),
            ('denial_of_access', True),
        ]
        for i in range(50):
            k = random.random()
            if k < 0.6:
                num_kinds = 1
            elif k < 0.9:
                num_kinds = 2
            else:
                num_kinds = 3
            kinds = dict(random.sample(incident_kinds, num_kinds))

            for key, _ in kinds.items():
                if key == 'arrest':
                    category = lookup_category('Arrest / Detention')
                elif key == 'equipment_seizure':
                    category = lookup_category('Equipment Search, Seizure, or Damage')
                elif key == 'border_stop':
                    category = lookup_category('Border Stop / Denial of Entry')
                elif key == 'physical_assault':
                    category = lookup_category('Physical Assaults')
                elif key == 'leak_prosecution':
                    category = lookup_category('Leak Prosecutions')
                elif key == 'subpoena':
                    category = lookup_category('Subpeonas')
                elif key == 'legal_order_for_records':
                    category = lookup_category('US Precident Cited Abroad')
                elif key == 'prior_restraint':
                    category = lookup_category('Subpeonas')
                elif key == 'denial_of_access':
                    category = lookup_category('US Precident Cited Abroad')
                else:
                    category = lookup_category('Documented Cases of Surveillance')
            IncidentPageFactory(
                parent=index,
                categories=[IncidentCategorization(category=category)],
                **kinds
            )
            # index.add_child(instance=page)
