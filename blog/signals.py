from django.db.models.signals import post_save, post_delete
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache

from blog.models import BlogIndexPage, BlogPage


def purge_blog_index_page_frontend_cache(**kwargs):
    """
    This function is very generous with how blog index page caches get purged.
    If we wanted to be more conservative we could rewrite this function to
    only purge a blog index page when one of its live children gets changed.

    """

    for page in BlogIndexPage.objects.all():
        purge_page_from_cache(page)


post_save.connect(purge_blog_index_page_frontend_cache, sender=BlogPage)
post_delete.connect(purge_blog_index_page_frontend_cache, sender=BlogPage)
