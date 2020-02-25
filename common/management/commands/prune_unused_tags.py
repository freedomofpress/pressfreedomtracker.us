from django.core.management.base import BaseCommand

from common.models import CommonTag


class Command(BaseCommand):
    help = 'Delete tags that are not applied to any incidents'

    def handle(self, *args, **options):
        CommonTag.objects.unused().delete()
