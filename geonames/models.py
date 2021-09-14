from django.db import models


class Country(models.Model):
    isocode = models.IntegerField(primary_key=True)
    iso = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    fips = models.TextField(null=True)
    name = models.TextField(null=True)
    capital = models.TextField(null=True)
    geonameid = models.BigIntegerField(null=True)


class Region(models.Model):
    isocode = models.ForeignKey(Country, db_column='isocode', on_delete=models.PROTECT)
    regcode = models.TextField()
    name = models.TextField(null=True)
    geonameid = models.BigIntegerField(primary_key=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['isocode', 'regcode'], name='unique_country_and_region')
        ]


class District(models.Model):
    name = models.TextField(null=True)
    geonameid = models.BigIntegerField(primary_key=True)

    isocode = models.ForeignKey(Country, db_column='isocode', on_delete=models.PROTECT)
    regcode = models.TextField()
    discode = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['isocode', 'regcode', 'discode'], name='unique_district_and_region')
        ]


class GeoName(models.Model):
    geonameid = models.BigIntegerField(primary_key=True)
    name = models.TextField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    isocode = models.ForeignKey(Country, null=True, db_column='isocode', on_delete=models.PROTECT)
    regcode = models.TextField(null=True)
    discode = models.TextField(null=True)

    population = models.BigIntegerField(null=True)
    elevation = models.BigIntegerField(null=True)
