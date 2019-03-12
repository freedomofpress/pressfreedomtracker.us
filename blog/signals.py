from django.db.models.signals import post_delete
from wagtail.core.signals import page_published
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache

from blog.models import BlogIndexPage, BlogPage
from cloudflare.utils import purge_tags_from_cache


def purge_blog_index_page_frontend_cache(**kwargs):
    """
    This function is very generous with how blog index page caches get purged.
    If we wanted to be more conservative we could rewrite this function to
    only purge a blog index page when one of its live children gets changed.

    """

    tags = []
    for page in BlogIndexPage.objects.all():
        tags.append(page.get_cache_tag())
        purge_page_from_cache(page)
    purge_tags_from_cache(tags)


page_published.connect(purge_blog_index_page_frontend_cache, sender=BlogPage)
post_delete.connect(purge_blog_index_page_frontend_cache, sender=BlogPage)
