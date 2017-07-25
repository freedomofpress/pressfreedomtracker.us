from django.apps import AppConfig


class IncidentConfig(AppConfig):
    name = 'incident'

    def ready(self):
        import incident.signals # noqa: F401
