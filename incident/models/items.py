from django.db import models

from common.validators import validate_disallow_AND
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable
from wagtailautocomplete.edit_handlers import AutocompletePanel


class Journalist(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        validate_disallow_AND(value)
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(max_length=255, validators=[validate_disallow_AND])

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Institution(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        validate_disallow_AND(value)
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(
        max_length=255, unique=True, validators=[validate_disallow_AND]
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class GovernmentWorker(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        validate_disallow_AND(value)
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(
        max_length=255, unique=True, validators=[validate_disallow_AND]
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        verbose_name = "Alleged recipient of leak"
        verbose_name_plural = "Alleged recipients of leaks"


class LawEnforcementOrganization(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        verbose_name = "Law enforcement organization"
        verbose_name_plural = "Law enforcement organizations"


class TargetedJournalist(Orderable):
    incident = ParentalKey(
        "incident.IncidentPage",
        on_delete=models.CASCADE,
        related_name="targeted_journalists",
    )

    journalist = models.ForeignKey(
        Journalist, on_delete=models.CASCADE, related_name="targeted_incidents"
    )

    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def summary(self):
        journalist = self.journalist.title
        if self.institution:
            return "{journalist} ({institution})".format(
                journalist=journalist,
                institution=self.institution.title,
            )
        return journalist

    panels = [
        AutocompletePanel("journalist", "incident.Journalist"),
        AutocompletePanel("institution", "incident.Institution"),
    ]


class Charge(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        validate_disallow_AND(value)
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_disallow_AND],
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class Nationality(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        validate_disallow_AND(value)
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_disallow_AND],
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "nationalities"


class PoliticianOrPublic(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        validate_disallow_AND(value)
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_disallow_AND],
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        verbose_name = "Politician or public figure"
        verbose_name_plural = "politicians or public figures"


class Venue(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        instance = kls(title=value)
        instance.full_clean()
        instance.save()
        return instance

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
