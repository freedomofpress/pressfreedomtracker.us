from django.db.models import TextChoices


class BlogTemplateType(TextChoices):
    DEFAULT = 'default', 'Default Blog'
    NEWSLETTER = 'newsletter', 'Newsletter'
    SPECIAL = 'special', 'Special Blog'
