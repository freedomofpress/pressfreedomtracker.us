from wagtail.contrib.frontend_cache.utils import PurgeBatch
from wagtail.signals import page_published, page_unpublished

from structlog import get_logger

from blog.models import BlogIndexPage, BlogPage
from cloudflare.utils import purge_tags_from_cache


logger = get_logger()


def purge_blog_index_page_frontend_cache(**kwargs):
    """
    This function is very generous with how blog index page caches get purged.
    If we wanted to be more conservative we could rewrite this function to
    only purge a blog index page when one of its live children gets changed.

    """

    tags = []
    batch = PurgeBatch()
    for page in BlogIndexPage.objects.all():
        tags.append(page.get_cache_tag())
        batch.add_page(page)
        logger.info(
            f"Purged page BlogIndexPage with title: {page.title} and slug: {page.slug}"
        )
    batch.purge()
    purge_tags_from_cache(tags)


page_published.connect(purge_blog_index_page_frontend_cache, sender=BlogPage)
page_unpublished.connect(purge_blog_index_page_frontend_cache, sender=BlogPage)
