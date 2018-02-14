from unittest import TestCase

from statistics.registry import Statistics


class RegisterTest(TestCase):
    def test_args_not_allowed(self):
        statistics = Statistics()
        with self.assertRaises(TypeError, msg='Statistics functions must have only positional or keyword arguments'):
            statistics.statistic({}, 'name', lambda *args: None)

    def test_kwargs_not_allowed(self):
        statistics = Statistics()
        with self.assertRaises(TypeError, msg='Statistics functions must have only positional or keyword arguments'):
            statistics.statistic({}, 'name', lambda **kwargs: None)
