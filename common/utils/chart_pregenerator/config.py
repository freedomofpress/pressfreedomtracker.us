from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured


class Settings:
    def __init__(self):
        self.settings = getattr(django_settings, 'CHART_PREGENERATOR', {})

    @property
    def host(self):
        return self.settings.get('HOST')

    @property
    def port(self):
        return self.settings.get('PORT')

    def validate(self):
        if not isinstance(self.port, int):
            raise ImproperlyConfigured('PORT must be an integer')
        if not isinstance(self.host, str):
            raise ImproperlyConfigured('HOST must be a string')


settings = Settings()
