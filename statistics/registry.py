NUMBERS = {}
MAPS = {}
VISUALIZATIONS = {}


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

        # TODO: potentially add it to template.Library() also.
        store[name] = fn

    def number(self, name=None, fn=None):
        return self.statistic(NUMBERS, name=name, fn=fn)

    def map(self, name=None, fn=None):
        return self.statistic(MAPS, name=name, fn=fn)

    def visualization(self, cls):
        VISUALIZATIONS[cls.template_name] = cls


def get_numbers():
    """Return registered statstics names and functions with number values"""
    return NUMBERS


def get_numbers_choices():
    for name in get_numbers().keys():
        yield (name, name)


def get_maps():
    """Return registered statstics names and functions with map values"""
    return MAPS


def get_maps_choices():
    return [(name, name) for name in get_maps().keys()]


def get_stats():
    """Return registered statstics names and functions with any value"""
    stats = NUMBERS.copy()
    stats.update(MAPS)
    return stats


def get_stats_choices():
    return [
        (name, '{} ({})'.format(name, 'Map' if name in MAPS else 'Number'))
        for name in get_stats().keys()
    ]


def get_visualization_choices():
    return [
        (visualization.template_name, visualization.verbose_name)
        for visualization in VISUALIZATIONS.values()
    ]
