def get_tags():
    """Get tag names and IDs in a form appropriate for model choices"""
    from common.models import CommonTag  # Avoids circular import

    return [(tag.title, tag.title) for tag in CommonTag.objects.all()]


def get_categories():
    """Get category names in a form appropriate for model choices"""
    from common.models import CategoryPage  # Avoids circular import

    return [
        (page.title, page.title) for page
        in CategoryPage.objects.order_by('title').live()
    ]


def get_states():
    """Get state names and abbreviations in a form appropriate for model choices"""
    from incident.models import State  # Avoids circular import

    return [
        (state.abbreviation, state.name) for state in State.objects.order_by('name')
    ]
