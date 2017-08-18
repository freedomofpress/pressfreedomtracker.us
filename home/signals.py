from django.db.models.signals import post_save, post_delete
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache

from common.models import CategoryPage
from home.models import HomePage
from incident.models import IncidentPage, IncidentIndexPage
from blog.models import BlogPage, BlogIndexPage


def purge_homepage_from_frontend_cache(**kwargs):
    for home_page in HomePage.objects.live():
        purge_page_from_cache(home_page)


# We're being very generous with which signals cause invalidation. If we need
# more aggressive caching, we could narrow these down, either in these
# connections or by adding some conditionals to the receiver function
# (e.g., only purge if the sender is actually going to appear on the homepage)
post_save.connect(purge_homepage_from_frontend_cache, sender=CategoryPage)
post_save.connect(purge_homepage_from_frontend_cache, sender=IncidentPage)
post_save.connect(purge_homepage_from_frontend_cache, sender=IncidentIndexPage)
post_save.connect(purge_homepage_from_frontend_cache, sender=BlogPage)
post_save.connect(purge_homepage_from_frontend_cache, sender=BlogIndexPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=CategoryPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=IncidentPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=IncidentIndexPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=BlogPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=BlogIndexPage)
