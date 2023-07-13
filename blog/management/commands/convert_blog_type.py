from django.core.management.base import BaseCommand

from blog.models import BlogPage
from blog.choices import BlogTemplateType


class Command(BaseCommand):
    help = 'Bulk update blog pages to use another template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Commit changes to the database',
        )

        parser.add_argument(
            'select',
            metavar='REGEX',
            help='Regular expression to select page titles to convert'
        )

        parser.add_argument(
            'template_type',
            choices=[choice[0] for choice in BlogTemplateType.choices],
            help='Template type to convert pages to',
        )

    def handle(self, *args, **options):
        select_regex = options['select']
        pages = BlogPage.objects.filter(title__regex=select_regex)
        selected_count = pages.count()
        self.stdout.write(
            f'Blog page titles matching {select_regex!r}: {selected_count}'
        )

        if selected_count < 1:
            return
        longest_title = max(len(page.title) for page in pages)
        top_row = f'{"id":^4} | {"title":^{longest_title}} | current type'

        self.stdout.write(top_row)
        self.stdout.write('-' * len(top_row))
        for i, page in enumerate(pages):
            self.stdout.write(f'{page.pk:>4} | {page.title:<{longest_title}} | {page.blog_type}')
            page.blog_type = options['template_type']
        self.stdout.write('\n')

        if options['commit']:
            BlogPage.objects.bulk_update(pages, ['blog_type'])
            self.stdout.write('Pages updated')
