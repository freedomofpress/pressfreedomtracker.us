from xmlrunner.extra.djangotestrunner import XMLTestRunner
import factory.random

from django.conf import settings
from django.test import TestCase
from django.test.runner import DiscoverRunner


def _install_wagtail_site_cache_reset():
    # Wagtail caches site root paths in process memory. Tests that delete or
    # replace the default Site (commonly via `Page.objects.filter(slug="home").delete()`
    # in setUpTestData) populate the cache with the new Site's id, but the
    # transaction rollback at class teardown reverts the DB without firing the
    # signals that would clear the cache. A later test then resolves page URLs
    # against a Site id that no longer exists and raises Site.DoesNotExist.
    # Clearing the cache after every test guarantees a cold cache for the next.
    from wagtail.models import Site

    original_post_teardown = TestCase._post_teardown

    def post_teardown(self):
        original_post_teardown(self)
        Site.clear_site_root_paths_cache()

    TestCase._post_teardown = post_teardown


class WithSeedMixin(object):
    """Modifies a test runner class to use a given constant from
    `settings.RANDOM_SEED` to seed the generation of randomized
    factory objects.

    """

    def setup_test_environment(self):
        seed = settings.RANDOM_SEED
        if seed:
            factory.random.reseed_random(seed)
            print(f"Using seed: {seed}")
        _install_wagtail_site_cache_reset()
        super().setup_test_environment()


class SeededXMLRunner(WithSeedMixin, XMLTestRunner):
    pass


class SeededDiscoveryRunner(WithSeedMixin, DiscoverRunner):
    pass
