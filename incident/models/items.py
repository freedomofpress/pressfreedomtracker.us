from django.db import models
from modelcluster.models import ClusterableModel


class Target(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title


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
