from django.db import models

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.core.models import Orderable
from wagtailautocomplete.edit_handlers import AutocompletePanel


class Target(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    JOURNALIST = 'Journalist'
    INSTITUTION = 'Institution'
    TYPE_TARGET = [
        ('JOURNALIST', 'Journalist'),
        ('INSTITUTION', 'Institution')]

    kind = models.CharField(
        choices=TYPE_TARGET,
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Journalist(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Institution(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class GovernmentWorker(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Government employee or contractor'
        verbose_name_plural = 'Government employees or contractors'


class TargetedJournalist(Orderable):
    incident = ParentalKey('incident.IncidentPage', on_delete=models.CASCADE, related_name='targeted_journalists')

    journalist = models.ForeignKey(Journalist, on_delete=models.CASCADE, related_name='targeted_incidents')

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    panels = [
        AutocompletePanel('journalist', 'incident.Journalist'),
        AutocompletePanel('institution', 'incident.Institution'),
    ]


class Charge(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Nationality(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'nationalities'


class PoliticianOrPublic(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'Politician or public figure'
        verbose_name_plural = 'politicians or public figures'


class Venue(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
