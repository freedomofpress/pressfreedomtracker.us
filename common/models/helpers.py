def get_tags():
    """Get tag names and IDs in a form appropriate for model choices"""
    from common.models import CommonTag  # Avoids circular import

    return [(tag.title, tag.title) for tag in CommonTag.objects.all()]
