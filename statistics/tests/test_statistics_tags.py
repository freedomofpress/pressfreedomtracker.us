import datetime

from django.core.exceptions import ValidationError
from django.template import (
    TemplateSyntaxError,
)
from django.test import TestCase

from common.tests.factories import CategoryPageFactory
from common.validators import TemplateValidator
from common.templatetags.render_as_template import render_as_template
from incident.tests.factories import (
    IncidentPageFactory,
    InstitutionFactory,
    TargetedJournalistFactory,
)
from statistics.templatetags.statistics_tags import (
    incidents_in_year_range_by_month,
)


class NumIncidentsTest(TestCase):
    """Test that num_incidents tag """
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory()
        cls.incident = IncidentPageFactory(
            title='hello',
            date=datetime.date(2017, 1, 1),
            categories=[cls.category],
        )
        cls.old_incident = IncidentPageFactory(
            title='goodbye',
            date=datetime.date(2016, 1, 1),
        )

    def setUp(self):
        self.validator = TemplateValidator()

    def test_gets_no_kwargs(self):
        """Not valid template tag"""
        template_string = '{% num_incidents 200 %}'
        with self.assertRaises(TemplateSyntaxError):
            render_as_template(template_string)
        with self.assertRaises(ValidationError):
            self.validator(template_string)

    def test_gets_no_args(self):
        """Not valid template tag"""
        template_string = '{% num_incidents %}'
        self.validator(template_string)
        result = render_as_template(template_string)
        self.assertEqual(result, '2')

    def test_gets_valid_search(self):
        """Valid template tag with constant search param"""
        template_string = '{% num_incidents search="hello" %}'
        self.validator(template_string)
        result = render_as_template(template_string)
        self.assertEqual(result, '1')

    def test_gets_variable_param(self):
        """Valid template tag with missing variable search param"""
        template_string = '{% num_incidents search=hello %}'
        with self.assertRaises(ValidationError):
            self.validator(template_string)
        result = render_as_template(template_string)
        self.assertEqual(result, '2')

    def test_manyrelationfilter_gets_integer_id(self):
        """Valid template tag with integer id instead of string"""
        template_string = '{{% num_incidents categories={} %}}'.format(self.category.id)
        self.validator(template_string)
        result = render_as_template(template_string)
        self.assertEqual(result, '1')

    def test_relationfilter_gets_integer_id(self):
        """Valid template tag with integer id instead of string"""
        template_string = '{% num_incidents state=1 %}'
        self.validator(template_string)
        result = render_as_template(template_string)
        self.assertEqual(result, '0')

    def test_gets_invalid_dates(self):
        """Valid tag but not valid params"""
        template_string = '{% num_incidents date_lower="2018-01-01" date_upper="2017-01-01" %}'
        result = render_as_template(template_string)
        self.assertEqual(result, '')
        with self.assertRaises(ValidationError):
            self.validator(template_string)

    def test_gets_valid_dates(self):
        """Valid tag but not valid params"""
        template_string = '{% num_incidents date_lower="2015-06-01" date_upper="2016-06-01" %}'
        self.validator(template_string)
        result = render_as_template(template_string)
        self.assertEqual(result, '1')


class NumTargetsTest(TestCase):
    def setUp(self):
        self.custody = 'CUSTODY'
        self.returned_full = 'RETURNED_FULL'
        self.category = CategoryPageFactory(
            title='Equipment Search or Seizure',
            incident_filters=['status_of_seized_equipment'],
        )
        self.validator = TemplateValidator()

    def test_invalid_args_validated(self):
        # Matched incident page
        template_string = '{{% num_targets categories={} status_of_seized_equipment={} %}}'.format(
            str(self.category.id),
            self.custody,
        )
        with self.assertRaises(ValidationError):
            self.validator(template_string)

    def test_target_count__filtered(self):
        # Matched incident page
        IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
            institution_targets=3,
            journalist_targets=0,
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
            institution_targets=5,
            journalist_targets=0,
        )
        template_string = '{{% num_targets categories={} status_of_seized_equipment="{}" %}}'.format(
            str(self.category.id),
            self.custody,
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '3')

    def test_target_count__combined(self):
        IncidentPageFactory(
            categories=[self.category],
            institution_targets=3,
            journalist_targets=0,
        )
        IncidentPageFactory(
            categories=[self.category],
            institution_targets=5,
            journalist_targets=0,
        )
        template_string = '{{% num_targets categories={} %}}'.format(
            str(self.category.id),
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '8')

    def test_target_count__combined_kinds(self):
        IncidentPageFactory(
            title='x1',
            categories=[self.category],
            institution_targets=2,
            journalist_targets=0,
        )
        IncidentPageFactory(
            title='x2',
            categories=[self.category],
            institution_targets=0,
            journalist_targets=2,
        )
        template_string = '{{% num_targets categories={} %}}'.format(
            str(self.category.id),
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '4')


class TestIncidentsInMultiValue(TestCase):
    """ Test that incidents with MultiValueFilter work """
    def setUp(self):
        self.pending = 'PENDING'
        self.dropped = 'DROPPED'
        self.category = CategoryPageFactory(
            title='Subpoena / Legal Order',
            incident_filters=['subpoena_statuses'],
        )
        self.validator = TemplateValidator()

    def test_invalid_args_validated(self):
        # Matched incident page
        template_string = '{{% num_journalist_targets categories={} subpoena_statuses={} %}}'.format(
            str(self.category.id),
            self.pending,
        )
        with self.assertRaisesRegex(ValidationError, 'wrapped in quotation marks'):
            self.validator(template_string)

    def test_target_count__filtered(self):
        # Matched incident page
        IncidentPageFactory(
            subpoena_statuses=[self.pending],
            categories=[self.category],
            institution_targets=3,
        )
        IncidentPageFactory(
            subpoena_statuses=[self.dropped],
            categories=[self.category],
            institution_targets=5,
        )
        template_string = '{{% num_institution_targets categories={} subpoena_statuses="{}" %}}'.format(
            str(self.category.id),
            self.pending,
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '3')

    def test_target_multiple_choice(self):
        IncidentPageFactory(
            subpoena_statuses=[self.pending],
            categories=[self.category],
            institution_targets=3,
        )
        IncidentPageFactory(
            subpoena_statuses=[self.dropped],
            categories=[self.category],
            institution_targets=5,
        )
        template_string = '{{% num_institution_targets categories={} subpoena_statuses="{},{}" %}}'.format(
            str(self.category.id),
            self.pending,
            self.dropped,
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '8')


class NumInstitutionTargetsTest(TestCase):
    def setUp(self):
        self.custody = 'CUSTODY'
        self.returned_full = 'RETURNED_FULL'
        self.category = CategoryPageFactory(
            title='Equipment Search or Seizure',
            incident_filters=['status_of_seized_equipment'],
        )
        self.validator = TemplateValidator()

    def test_invalid_args_should_raise_validation_error(self):
        template_string = '{{% num_institution_targets categories={} status_of_seized_equipment={} %}}'.format(
            str(self.category.pk),
            self.custody,
        )
        with self.assertRaisesRegex(ValidationError, 'wrapped in quotation marks'):
            self.validator(template_string)

    def test_target_count__filtered(self):
        # Matched incident page
        IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
            institution_targets=3,
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
            institution_targets=5,
        )
        template_string = '{{% num_institution_targets categories={} status_of_seized_equipment="{}" %}}'.format(
            str(self.category.id),
            self.custody,
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '3')

    def test_target_count__combined(self):
        IncidentPageFactory(
            categories=[self.category],
            institution_targets=3,
        )
        IncidentPageFactory(
            categories=[self.category],
            institution_targets=5,
        )
        template_string = '{{% num_institution_targets categories={} %}}'.format(
            str(self.category.id),
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '8')

    def test_target_count__deduped(self):
        inst1 = InstitutionFactory()
        inst2 = InstitutionFactory()
        incident1 = IncidentPageFactory(
            categories=[self.category],
            institution_targets=0,
        )
        incident1.targeted_institutions.set([inst1, inst2])
        incident1.save()

        incident2 = IncidentPageFactory(
            categories=[self.category],
            institution_targets=0,
        )
        incident2.targeted_institutions = [inst1]
        incident2.save()

        template_string = '{{% num_institution_targets categories={} %}}'.format(
            str(self.category.id),
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '2')


class NumJournalistTargetsTest(TestCase):
    def setUp(self):
        self.custody = 'CUSTODY'
        self.returned_full = 'RETURNED_FULL'
        self.category = CategoryPageFactory(
            title='Equipment Search or Seizure',
            incident_filters=['status_of_seized_equipment'],
        )
        self.validator = TemplateValidator()

    def test_invalid_args_should_raise_validation_error(self):
        template_string = '{{% num_journalist_targets categories={} status_of_seized_equipment={} %}}'.format(
            str(self.category.pk),
            self.custody,
        )
        with self.assertRaisesRegex(ValidationError, 'wrapped in quotation marks'):
            self.validator(template_string)

    def test_target_count__filtered(self):
        TargetedJournalistFactory(
            incident__categories=[self.category],
            incident__status_of_seized_equipment=self.returned_full,
        )
        TargetedJournalistFactory(
            incident__categories=[self.category],
            incident__status_of_seized_equipment=self.custody,
        )

        template_string = '{{% num_journalist_targets categories={} status_of_seized_equipment="{}" %}}'.format(
            str(self.category.id),
            self.custody,
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '1')

    def test_target_count__combined(self):
        TargetedJournalistFactory.create_batch(
            5,
            incident__categories=[self.category],
            incident__status_of_seized_equipment=self.returned_full,
        )

        template_string = '{{% num_journalist_targets categories={} %}}'.format(
            str(self.category.id),
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '5')

    def test_target_count__deduped(self):
        tj = TargetedJournalistFactory(
            incident__categories=[self.category],
        )
        TargetedJournalistFactory(
            incident__categories=[self.category],
        )
        TargetedJournalistFactory(
            incident__categories=[self.category],
            journalist=tj.journalist,
        )

        template_string = '{{% num_journalist_targets categories={} %}}'.format(
            str(self.category.id),
        )
        self.validator(template_string)
        rendered = render_as_template(template_string)
        self.assertEqual(rendered, '2')


class TestIncidentsInYearRangeByMonth(TestCase):
    """Test that incidents_in_year_range_by_month tag """
    @classmethod
    def setUpTestData(cls):
        IncidentPageFactory(date=datetime.date(2017, 1, 1))
        IncidentPageFactory(date=datetime.date(2017, 2, 1))
        IncidentPageFactory(date=datetime.date(2016, 1, 1))
        IncidentPageFactory(date=datetime.date(2015, 1, 1))

    def assert_is_map(self, obj):
        """Assert that an object is a statistics map object

        This function will raise an AssertionError if the given object
        is not a "statistical map", i.e. a list of 2-tuples or an empty
        list.

        """
        self.assertIsInstance(obj, list)
        for item in obj:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)

    def test_should_be_type_map(self):
        """should return a map."""
        incidents = incidents_in_year_range_by_month(2016, 2017)
        self.assert_is_map(incidents)
