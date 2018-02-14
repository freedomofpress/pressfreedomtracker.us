from inspect import Parameter
import inspect


_numbers = {}
_maps = {}


class Statistics(object):
    def statistic(self, store, name=None, fn=None):
        """Register a statistics function as usable elsewhere on the site"""
        if name is None and fn is None:
            def decorator(fn):
                self.statistic(store, name, fn)
                return fn
            return decorator

        if name is not None and fn is None:
            if callable(name):
                fn_name = getattr(name, "_decorated_function", name).__name__
                self.statistic(store, name=fn_name, fn=name)
                return name

        # We don't handle *args or **kwargs yet. If support for these is added,
        # also update statistics cleaning.
        signature = inspect.signature(fn)
        if any(param.kind != Parameter.POSITIONAL_OR_KEYWORD for param in signature.parameters.values()):
            raise TypeError('Statistics functions must have only positional or keyword arguments')

        # TODO: potentially add it to template.Library() also.
        store[name] = fn

    def number(self, name=None, fn=None):
        return self.statistic(_numbers, name=name, fn=fn)

    def map(self, name=None, fn=None):
        return self.statistic(_maps, name=name, fn=fn)


def get_numbers():
    """Return registered statstics names and functions with number values"""
    return _numbers


def get_numbers_choices():
    return [(name, name) for name in get_numbers().keys()]


def get_maps():
    """Return registered statstics names and functions with map values"""
    return _maps


def get_maps_choices():
    return [(name, name) for name in get_maps().keys()]


def get_stats():
    """Return registered statstics names and functions with any value"""
    stats = _numbers.copy()
    stats.update(_maps)
    return stats


def get_stats_choices():
    return [(name, name) for name in get_stats().keys()]
