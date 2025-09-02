from django.core.management.base import BaseCommand
from django.db.models import Count

from taggit.models import Tag


class Command(BaseCommand):
    help = 'Delete wagtail tags that are not applied to any items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Commit changes to the database',
        )

    def handle(self, *args, **options):
        tags = Tag.objects.annotate(item_count=Count('taggit_taggeditem_items')).filter(item_count=0)

        if options['commit']:
            tags.delete()
            self.stdout.write('Tags deleted')
        elif not tags:
            self.stdout.write('No unused wagtail tags found')
        else:
            self.stdout.write(f'Found {len(tags)}:')
            for tag in tags:
                self.stdout.write(f'* {tag.name}')
