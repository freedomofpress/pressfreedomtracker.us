from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.models import CategoryPage
from incident.models import IncidentIndexPage
from common.tests.factories import (
    PersonPageFactory,
)
from incident.tests.factories import (
    MultimediaIncidentPageFactory, IncidentPageFactory, VenueFactory,
)


FACTORY_ARGS_BY_FOR_CATEGORY = {
    'arrest': {
        'arrest': True,
        'current_charges': 2,
        'dropped_charges': 2,
    }
}


class Command(BaseCommand):
    help = 'Create randomized incidents for testing'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'categories',
            nargs='+',
            type=str,
            choices=[
                'arrest',
                'border_stop',
                'denial_of_access',
                'equipment_search',
                'physical_attack',
                'leak_case',
                'subpoena',
                'equipment_damage',
                'prior_restraint',
                'chilling_statement',
                'other_incident',
            ]
        )
        data_group = parser.add_argument_group(
            'Incident Data options',
            'Options that can apply to all incidents being created.'
        )

        general_group = parser.add_argument_group(
            'General options',
            'How many and what type of incidents will be created',
        )

        general_group.add_argument(
            '--media', action='store_true',
            help="When this flag is used, existing images in the wagtail database will be used as the incident's teaser image and in the page's body content.",
        )
        general_group.add_argument(
            '-n', '--number', default=1, type=int, metavar='NUM',
            help='Generate NUM incidents',
        )

        arrest_group = parser.add_argument_group(
            'Arrest options',
            'options that apply to incidients created in the "arrest" category.',
        )
        arrest_group.add_argument(
            '--current-charges', default=2, type=int, metavar='NUM',
            help='Generate NUM current charges.'
        )
        arrest_group.add_argument(
            '--dropped-charges', default=2, type=int, metavar='NUM',
            help='Generate NUM dropped charges.',
        )

        border_group = parser.add_argument_group(
            'Border Stop options',
            'options that apply to incidients created in the "border stop" category.',
        )
        border_group.add_argument(
            '--target-nationalities', default=2, type=int, metavar='NUM',
            help='Generate NUM nationalities.'
        )

        denial_group = parser.add_argument_group(
            'Denial of Access options',
            'options that apply to incidients created in the "denial of access" category.',
        )
        denial_group.add_argument(
            '--politicians', default=2, type=int, metavar='NUM',
            help='Generate NUM politicians/public figures.',
        )

        leak_group = parser.add_argument_group(
            'Leak Case options',
            'options that apply to incidients created in the "Leak Case" category.',
        )
        leak_group.add_argument(
            '--workers', default=2, type=int, metavar='NUM',
            help='Generate NUM workers whose communications were obtained.',
        )

        data_group.add_argument(
            '--gen-venues', default=2, type=int, metavar='NUM',
            help='Generate NUM venues.',
        )
        data_group.add_argument(
            '--venue', action='append', metavar='NAME',
            help='Use venue named NAME (in addition to other randomized venues).  This flag may be provided multiple times.',
        )

        data_group.add_argument(
            '--gen-authors', default=2, type=int, metavar='NUM',
            help='Generate NUM authors.',
        )
        data_group.add_argument(
            '--author', action='append', metavar='NAME',
            help='Use author named NAME (in addition to other randomized authors).  This flag may be provided multiple times.',
        )

        data_group.add_argument(
            '--gen-journalists', default=2, type=int, metavar='NUM',
            help='Generate NUM targeted journalists.',
        )
        data_group.add_argument(
            '--gen-institutions', default=2, type=int, metavar='NUM',
            help='Generate NUM targeted institutions.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            index = IncidentIndexPage.objects.get()
        except (IncidentIndexPage.DoesNotExist, IncidentIndexPage.MultipleObjectsReturned):
            raise CommandError('Could not find a single incident index page, aborting.')

        factory_argset = {
            'arrest': {
                'arrest': True,
                'current_charges': options['current_charges'],
                'dropped_charges': options['dropped_charges'],
            },
            'border_stop': {
                'border_stop': True,
                'target_nationality': options['target_nationalities'],
            },
            'denial_of_access': {
                'politicians_or_public_figures_involved': options['politicians'],
            },
            'equipment_search': {
                'equipment_search': True,
            },
            'physical_attack': {
                'physical_attack': True,
            },
            'leak_case': {
                'leak_case': True,
                'workers_whose_communications_were_obtained': options['workers'],
            },
            'subpoena': {
                'subpoena': True,
            },
            'equipment_damage': {
                'equipment_damage': True,
            },
            'prior_restraint': {
                'prior_restraint': True,
            },
            'chilling_statement': {},
            'other_incident': {},
        }

        venues = []
        if options['venue']:
            for venue_name in options['venue']:
                venues.append(VenueFactory(title=venue_name))
        venues.extend(VenueFactory.create_batch(options['gen_venues']))

        authors = []
        if options['author']:
            for author_name in options['author']:
                authors.append(PersonPageFactory(title=author_name))
        authors.extend(PersonPageFactory.create_batch(options['gen_authors']))

        if options['media']:
            factory = MultimediaIncidentPageFactory
        else:
            factory = IncidentPageFactory

        categories = []
        factory_args = {}
        for category in options['categories']:
            try:
                categories.append(CategoryPage.objects.get(slug=category))
            except CategoryPage.DoesNotExist:
                raise CommandError(f'Could not find category `{category}`')
            factory_args.update(factory_argset[category])

        result = factory.create_batch(
            options['number'],
            parent=index,
            categories=categories,
            authors=authors,
            venue=venues,
            journalist_targets=options['gen_journalists'],
            institution_targets=options['gen_institutions'],
            **factory_args,
        )
