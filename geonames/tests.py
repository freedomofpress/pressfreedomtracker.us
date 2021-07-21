from django.test import TestCase

from .cities import get_city_coords
from .models import Country, Region, GeoName


class CitiesTestCase(TestCase):
    def setUp(self):
        united_states = Country.objects.create(
            isocode=1,
            iso='US',
            iso3='USA',
            fips='US',
            name='United States',
            capital='Washington',
            geonameid=1,
        )

        Region.objects.create(
            isocode=united_states,
            regcode='AK',
            name='Alaska',
            geonameid=1,
        )

        self.geoname = GeoName.objects.create(
            geonameid=1,
            name='City X',
            latitude=1.0,
            longitude=2.0,
            isocode=united_states,
            regcode='AK',
        )

    def test_city_coords_lookup_by_name_and_state(self):
        self.assertEqual(
            get_city_coords(city=self.geoname.name, state=self.geoname.regcode),
            (self.geoname.latitude, self.geoname.longitude)
        )

    def test_city_coords_lookup_by_name_and_state_missing(self):
        self.assertEqual(
            get_city_coords(city='Missing', state=self.geoname.regcode),
            (None, None)
        )
