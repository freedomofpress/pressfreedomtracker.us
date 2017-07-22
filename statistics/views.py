import inspect

from django.shortcuts import render

from statistics.registry import get_maps, get_numbers


def introspect_func(name, f):
    return {
        'docstring': f.__doc__,
        'arguments': inspect.getargspec(f)[0],
        'name': name,
    }


def stats_guide_view(request):
    context = {
        'maps': [introspect_func(name, f) for name, f in get_maps().items()],
        'numbers': [introspect_func(name, f) for name, f in get_numbers().items()],
    }
    return render(request, 'statistics-guide.html', context)
