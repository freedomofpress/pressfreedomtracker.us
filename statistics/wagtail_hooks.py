from django.conf.urls import url
from django.core.urlresolvers import reverse

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from statistics.views import stats_guide_view


@hooks.register('register_admin_menu_item')
def register_stats_guide_menu_item():
    return MenuItem(
        'Statistics Guide',
        reverse('statistics_guide'),
        classnames='icon icon-folder-inverse',
        order=10000,
    )


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^stats_guide/$', stats_guide_view, name='statistics_guide'),
    ]
