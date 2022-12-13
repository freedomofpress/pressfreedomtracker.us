from factory import (
    Sequence,
    post_generation,
    Faker,
    Trait,
    LazyAttribute,
    SubFactory,
)
from factory.django import DjangoModelFactory
from wagtail.models import Page

from menus.models import Menu, MenuItem


class MenuItemFactory(DjangoModelFactory):
    class Meta:
        model = MenuItem

    sort_order = Sequence(int)
    text = Faker('sentence', nb_words=3, variable_nb_words=False)
    link_page = None
    link_document = None
    link_url = '#'
    html_title = ''
    html_classes = ''

    class Params:
        for_page = Trait(link_url='', text=LazyAttribute(lambda o: o.link_page.title))


class MenuFactory(DjangoModelFactory):
    class Meta:
        model = Menu

    name = Sequence(lambda n: "Menu {}".format(n))
    slug = Sequence(lambda n: "menu-{}".format(n))

    @post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for item in extracted:
                if isinstance(item, Page):
                    MenuItemFactory(
                        menu=self, link_page=item, text=item.title, link_url=''
                    )
                elif isinstance(item, dict):
                    MenuItemFactory(menu=self, text=item['text'], link_url=item['link'])


class MainMenuFactory(MenuFactory):
    class Meta:
        django_get_or_create = ('slug',)

    name = 'Main Menu'
    slug = 'main'  # this slug has special meaning in the site navigation template


class MainMenuItemFactory(MenuItemFactory):
    menu = SubFactory(MainMenuFactory)
