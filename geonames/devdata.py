import itertools
from collections.abc import Callable, Generator
from typing import TypeVar

from .models import Country, GeoName, Region


T = TypeVar("T")


def sequence(func: Callable[[int], T]) -> Generator[T]:
    """
    Generates a sequence of values from a sequence of integers starting at zero,
    passed through the callable, which must take an integer argument.
    """
    return (func(n) for n in itertools.count())


GEONAME_NAME_SEQUENCE = sequence(lambda n: f"City {n}")
GEONAME_ID_SEQUENCE = sequence(lambda n: n)
REGION_ID_SEQUENCE = sequence(lambda n: n)
REGCODE_SEQUENCE = sequence(lambda n: f"RG{n}")
REGION_NAME_SEQUENCE = sequence(lambda n: f"Region {n}")
ISOCODE_ID_SEQUENCE = sequence(lambda n: n)


def create_country(
    *,
    name: str = "United States",
    capital: str = "Washington",
    iso: str = "US",
    iso3: str = "USA",
    # isocode: int = 1,
):
    return Country.objects.create(
        isocode=next(ISOCODE_ID_SEQUENCE),
        iso=iso,
        iso3=iso3,
        name=name,
        capital=capital,
    )


def create_region(
    *,
    country: Country | None = None,
    regcode: str | None = None,
    name: str | None = None,
):
    return Region.objects.create(
        isocode=country or create_country(),
        regcode=regcode or next(REGCODE_SEQUENCE),
        name=name or next(REGION_NAME_SEQUENCE),
        geonameid=next(REGION_ID_SEQUENCE),
    )


def create_geoname(
    *,
    name: str = "",
    country: int | Country | None = None,
    region: str | None = None,
    latitude: float = 40.44062,
    longitude: float = -79.99589,
):
    if country is None:
        country = create_country()
    if region is None:
        region = create_region(country=country)
    else:
        region = create_region(regcode=region, country=country)
    return GeoName.objects.create(
        geonameid=next(GEONAME_ID_SEQUENCE),
        name=name or next(GEONAME_NAME_SEQUENCE),
        isocode=country,
        latitude=latitude,
        longitude=longitude,
        regcode=region.regcode,
    )
