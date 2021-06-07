from xmlrunner.extra.djangotestrunner import XMLTestRunner
import factory.random

from django.conf import settings
from django.test.runner import DiscoverRunner


class WithSeedMixin(object):
    """Modifies a test runner class to use a given constant from
    `settings.RANDOM_SEED` to seed the generation of randomized
    factory objects.

    """
    def setup_test_environment(self):
        seed = settings.RANDOM_SEED
        if seed:
            factory.random.reseed_random(seed)
            print(f'Using seed: {seed}')
        super().setup_test_environment()


class SeededXMLRunner(WithSeedMixin, XMLTestRunner):
    pass


class SeededDiscoveryRunner(WithSeedMixin, DiscoverRunner):
    pass
