_stats = {}


def statistic(name=None, fn=None):
    """Register a statistics function as usable elsewhere on the site"""
    if name is None and fn is None:
        def decorator(fn):
            statistic(name, fn)
            return fn
        return decorator

    if name is not None and fn is None:
        if callable(name):
            fn_name = getattr(name, "_decorated_function", name).__name__
            statistic(name=fn_name, fn=name)
            return name

    # TODO: potentially add it to template.Library() also.
    _stats[name] = fn


def get_stats():
    """Return registered statistics names and functions"""
    return _stats
