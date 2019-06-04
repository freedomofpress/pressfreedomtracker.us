import json
import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core import management
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from wagtail.core.models import Site
from wagtail.core.rich_text import RichText

from blog.models import BlogIndexPage
from blog.tests.factories import BlogIndexPageFactory, BlogPageFactory
from common.models import (
    CategoryPage,
    SimplePage, SimplePageWithSidebar,
    FooterSettings, CustomImage, SearchSettings,
)
from common.tests.factories import PersonPageFactory
from forms.models import FormPage
from home.models import HomePage, HomePageIncidents
from incident.models import IncidentCategorization, IncidentIndexPage, IncidentPage
from menus.models import Menu, MenuItem

LIPSUM = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut in erat orci. Pellentesque eget scelerisque felis, ut iaculis erat. Nullam eget quam felis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Vestibulum eu dictum ligula. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Praesent et mi tellus. Suspendisse bibendum mi vel ex ornare imperdiet. Morbi tincidunt ut nisl sit amet fringilla. Proin nibh nibh, venenatis nec nulla eget, cursus finibus lectus. Aenean nec tellus eget sem faucibus ultrices.'


class Command(BaseCommand):
    help = 'Creates data appropriate for development'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating development data... ', '')
        self.stdout.flush()

        # createcategories will handle creating homepage.
        management.call_command('createcategories')
        home_page = HomePage.objects.get(slug='home')

        if not Site.objects.filter(is_default_site=True):
            site = Site.objects.create(
                site_name='Press Freedom Incidents (Dev)',
                hostname='localhost',
                port='8000',
                root_page=home_page,
                is_default_site=True
            )
        else:
            site = Site.objects.get(
                is_default_site=True,
            )
        # ABOUT PAGE
        if not SimplePage.objects.filter(slug='about').exists():
            about_page = SimplePage(
                title='About',
                slug='about',
                body=json.dumps([
                    dict(
                        type='text',
                        value=dict(
                            text=LIPSUM,
                            background_color='white',
                            text_align='left',
                            font_size='large',
                            font_family='sans-serif',
                        ),
                    ),
                ])
            )
            home_page.add_child(instance=about_page)
            home_page.about_page = about_page
        else:
            about_page = SimplePage.objects.get(slug='about')

        # RESOURCES PAGE
        if not Menu.objects.filter(slug='resources').exists():
            resources_menu = Menu.objects.create(name='Resources Sidebar', slug='resources')
            MenuItem.objects.bulk_create([
                MenuItem(
                    text='About',
                    link_page=about_page,
                    menu=resources_menu,
                    sort_order=1
                ),
                MenuItem(
                    text='A menu item',
                    link_url='#',
                    menu=resources_menu,
                    sort_order=2
                ),
            ])
            resources_page = SimplePageWithSidebar(
                title='Resources',
                slug='resources',
                sidebar_menu=resources_menu,
                body=json.dumps([
                    dict(
                        type='text',
                        value=dict(
                            text=LIPSUM,
                            background_color='white',
                            text_align='left',
                            font_size='large',
                            font_family='sans-serif',
                        ),
                    ),
                ])
            )

            home_page.add_child(instance=resources_page)

        # SUBMIT INCIDENT FORM
        if not FormPage.objects.filter(slug='submit-incident'):
            incident_form = FormPage(title='Submit an incident', slug='submit-incident')
            home_page.add_child(instance=incident_form)
        else:
            FormPage.objects.get(slug='submit-incident')

        # CREATE MENUS
        # delete any the existing main menu
        if not Menu.objects.filter(slug='main').exists():
            main = Menu.objects.create(name='Main Menu', slug='main')
            MenuItem.objects.bulk_create([
                MenuItem(
                    text='About',
                    link_page=about_page,
                    menu=main,
                    sort_order=1
                ),
                MenuItem(
                    text='Resources',
                    link_page=resources_page,
                    menu=main,
                    sort_order=2
                ),
                MenuItem(
                    text='Contact',
                    link_url='#',
                    menu=main,
                    sort_order=3
                ),
                MenuItem(
                    text='Submit an Incident',
                    link_page=incident_form,
                    menu=main,
                    sort_order=4,
                    html_classes='header__nav-link--highlighted'
                ),
            ])

        footer_menu, created = Menu.objects.get_or_create(
            name='Footer Menu', slug='footer')
        if created:
            MenuItem.objects.bulk_create([
                MenuItem(
                    text='About',
                    link_page=about_page,
                    menu=footer_menu,
                    sort_order=1,
                ),
                MenuItem(
                    text='Our Partners',
                    link_url='#',
                    menu=footer_menu,
                    sort_order=2,
                ),
                MenuItem(
                    text='Privacy Policy',
                    link_url='#',
                    menu=footer_menu,
                    sort_order=3,
                ),
                MenuItem(
                    text='Contact',
                    link_url='#',
                    menu=footer_menu,
                    sort_order=4,
                ),
            ])

        # FOOTER
        footer_settings = FooterSettings.for_site(site)
        footer_settings.body = RichText('U.S. Press Freedom Tracker is a project of <a href="https://freedom.press">Freedom of the Press Foundation</a> and the <a href="https://www.cpj.org/">Committee to Protect Journalists</a>.')
        if footer_menu:
            footer_settings.menu = footer_menu
        footer_settings.save()

        # BLOG RELATED PAGES
        if not BlogIndexPage.objects.filter(slug='fpf-blog').exists():
            blog_index_page = BlogIndexPageFactory(parent=home_page)
            home_page.blog_index_page = blog_index_page

            author1, author2, author3 = PersonPageFactory.create_batch(3, parent=home_page)

            blog_text = dict(
                body__0__heading_1__content='Pizza',
                body__1__heading_2__content='Terminology',
                body__2__text__text=RichText('Pizza: noun, so good.'),
                body__2__text__background_color='white',
                body__2__text__text_align='left',
                body__2__text__font_size='large',
                body__2__text__font_family='sans-serif',
                body__3__heading_2__content='History',
                body__4__heading_3__content='Antiquity',
                body__5__heading_3__content='Medieval',
            )
            BlogPageFactory.create_batch(
                10,
                parent=blog_index_page,
                author=author1,
                **blog_text,
            )
            BlogPageFactory.create_batch(
                10,
                parent=blog_index_page,
                author=author2,
                **blog_text,
            )
            BlogPageFactory.create_batch(
                10,
                parent=blog_index_page,
                author=author3,
                **blog_text,
            )
        else:
            blog_index_page = BlogIndexPage.objects.get(slug='fpf-blog')

        # INCIDENT RELATED PAGES
        search_settings = SearchSettings.for_site(site)
        if not IncidentIndexPage.objects.filter(slug='all-incidents'):
            incident_index_page = IncidentIndexPage(
                title='All Incidents',
                slug='all-incidents'
            )
            home_page.add_child(instance=incident_index_page)

            for x in range(0, 100):
                page = IncidentPage(
                    title='Maecenas convallis sem malesuada nisl placerat volutpat{}'.format(x),
                    slug='maecenas-convallis-{}'.format(x),
                    date=timezone.now() - timedelta(x),
                    body=[(
                        'rich_text',
                        RichText('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut in erat orci. Pellentesque eget scelerisque felis, ut iaculis erat. Nullam eget quam felis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Vestibulum eu dictum ligula. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Praesent et mi tellus. Suspendisse bibendum mi vel ex ornare imperdiet. Morbi tincidunt ut nisl sit amet fringilla. Proin nibh nibh, venenatis nec nulla eget, cursus finibus lectus. Aenean nec tellus eget sem faucibus ultrices.')
                    )],
                )
                random_idx = random.randint(0, CategoryPage.objects.count() - 1)
                page.categories = [
                    IncidentCategorization(
                        category=CategoryPage.objects.all()[random_idx],
                        sort_order=0,
                    )
                ]
                incident_index_page.add_child(instance=page)
                if x == 0:
                    HomePageIncidents.objects.create(
                        sort_order=4,
                        page=home_page,
                        incident=page,
                    )
        else:
            incident_index_page = IncidentIndexPage.objects.get(slug='all-incidents')

        search_settings.search_page = incident_index_page
        search_settings.save()

        incident_data = [
            dict(
                title="BBC journalist questioned by US border agents, devices searched",
                body="Ali Hamedani, a reporter for BBC World Service, was detained at Chicago O'Hare airport for over two hours.",
            ),
            dict(
                title="Vocativ journalist charged with rioting in Washington",
                body="Police arrested Evan Engel, a senior producer at the news website Vocativ.",
            ),
            dict(
                title="Media outlets excluded from gaggle",
                body="At least nine news outlets were excluded from an informal briefing known as 'a gaggle' by President Donald Trump's White House Press Secretary Sean Spicer.",
            ),
        ]
        image = CustomImage.objects.filter(title='Sample Image').first()
        if not image:
            image = CustomImage.objects.create(
                title='Sample Image',
                file=ImageFile(open('styleguide/static/styleguide/voactiv.jpg', 'rb'), name='voactiv.jpg'),
                attribution='createdevdata'
            )
        for index, data in enumerate(incident_data):
            page = IncidentPage(
                title=data['title'],
                body=[('rich_text', RichText('<p>{}</p>'.format(data['body'])))],
                date=timezone.now() + timedelta(index + 1),
                teaser_image=image,
            )
            random_idx = random.randint(0, CategoryPage.objects.count() - 1)
            page.categories = [
                IncidentCategorization(
                    category=CategoryPage.objects.all()[random_idx],
                    sort_order=0,
                )
            ]
            incident_index_page.add_child(instance=page)
            HomePageIncidents.objects.create(
                sort_order=index + 1,
                page=home_page,
                incident=page,
            )

        home_page.save()

        # Create superuser
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                'test',
                'test@pressfreedom',
                'test',
            )
            self.stdout.write(
                'Superuser created:\n'
                '\tname: test\n'
                '\temail: test@pressfreedom\n'
                '\tpassword: test'
            )

        self.stdout.write('Done.')
