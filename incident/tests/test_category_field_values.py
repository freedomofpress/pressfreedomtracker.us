from django.test import TestCase

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    ChargeFactory,
)
from incident.models.choices import (
    ARREST_STATUS,
    DETENTION_STATUS,
    STATUS_OF_CHARGES,
    STATUS_OF_PRIOR_RESTRAINT,
    STATUS_OF_SEIZED_EQUIPMENT,
    SUBPOENA_STATUS,
)


class CategoryFieldValues(TestCase):
    """Category values"""
    def setUp(self):
        self.index = IncidentIndexPageFactory()
        self.category1 = CategoryPageFactory(
            **{'arrest': True}
        )
        self.category2 = CategoryPageFactory(
            **{'equipment_damage': True}
        )

        self.incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category1, self.category2],
            **{'arrest': True, 'equipment_damage': True}
        )
        charge = ChargeFactory()
        self.incident.current_charges.add(charge)
        self.incident.save()

        self.category_details = self.incident.get_category_details()

    def test_should_get_category_details(self):
        self.assertEqual(len(self.category_details.items()), 2)

    def test_should_get_basic_category_fields(self):
        arrest_details = self.category_details[self.category1]
        self.assertEqual(arrest_details[0]['name'], 'Arrest Status')
        self.assertIn(self.incident.arrest_status, arrest_details[0]['html'])

    def test_should_get_list_category_fields(self):
        arrest_details = self.category_details[self.category1]
        self.assertEqual(arrest_details[3]['name'], 'Current Charges')
        for current_charge in self.incident.current_charges.all():
            self.assertIn(current_charge.title, arrest_details[3]['html'])

    def test_should_get_equipment_list_category_fields(self):
        equipment_damage_details = self.category_details[self.category2]
        self.assertEqual(equipment_damage_details[0]['name'], 'Equipment Broken')
        for equipment_broken in self.incident.equipment_broken.all():
            self.assertIn(equipment_broken.equipment.name, equipment_damage_details[0]['html'])

    def test_should_get_date_category_fields(self):
        arrest_details = self.category_details[self.category1]
        self.assertEqual(arrest_details[5]['name'], 'Detention Date')
        self.assertIn(self.incident.detention_date.isoformat(), arrest_details[5]['html'])

    def test_should_get_boolean_category_fields(self):
        arrest_details = self.category_details[self.category1]
        self.assertEqual(arrest_details[7]['name'], 'Unnecessary use of force?')
        self.assertIn(str(self.incident.unnecessary_use_of_force), arrest_details[7]['html'])
