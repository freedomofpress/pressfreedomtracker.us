from .models import GeoName


def get_city_coords(city=None, state=None, iso3='USA'):
    """Returns a tuple of (latitude, longitude) values for the given city
    and state.

    Returns (None, None) if the city or state name cannot be located.
    If there is more than one match, the first is returned.  The
    country searched is the United States, by default, but that can be
    changed by passing an ISO 3166 country code as the third argument.

    See https://unstats.un.org/unsd/tradekb/Knowledgebase/Country-Code
    for more information.

    """
    city_coords = (None, None)

    if not city or not state:
        return city_coords

    latlong = GeoName.objects.filter(
        name=city,
        regcode=state,
        isocode__iso3=iso3
    ).values_list('latitude', 'longitude')

    if latlong:
        city_coords = latlong[0]

    return city_coords
