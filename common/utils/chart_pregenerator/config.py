from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property


class Settings:
    def __init__(self):
        self.settings = getattr(django_settings, 'CHART_PREGENERATOR', {})

    @property
    def host(self):
        return getattr(self.settings, 'HOST', 'node-chart-pregenerator')

    @cached_property
    def port(self):
        return int(getattr(settings, 'PORT', '3000'))

    def validate(self):
        try:
            self.port
        except (TypeError, ValueError):
            raise ImproperlyConfigured('PORT must be an integer')
        if not isinstance(self.host, str):
            raise ImproperlyConfigured('HOST must be a string')


settings = Settings()
