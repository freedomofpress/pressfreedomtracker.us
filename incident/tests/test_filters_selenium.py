import unittest
import urllib.parse
import itertools
from datetime import timedelta

from django.utils import timezone
from wagtail.models import Page, Site
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from common.tests.selenium import SeleniumTest
from common.tests.factories import CategoryPageFactory
from common.models.settings import (
    SearchSettings,
    IncidentFilterSettings,
    GeneralIncidentFilter,
)
from home.tests.factories import HomePageFactory
from incident.tests.factories import (
    IncidentIndexPageFactory,
    IncidentPageFactory,
    IncidentUpdateFactory,
    StateFactory,
    EquipmentFactory,
    EquipmentBrokenFactory,
)
from incident import choices
from incident.models import State


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s) + 1)
    )


@unittest.skip('Test applies to legacy templates')
class FilterTest(SeleniumTest):
    def setUp(self):
        super().setUp()

        self.root_page = Page.objects.get(slug='home')
        site = Site.objects.get(is_default_site=True)

        self.home_page = HomePageFactory(parent=self.root_page)

        # configure search to enable filter display
        search_settings = SearchSettings.for_site(site)
        self.index = IncidentIndexPageFactory(parent=self.root_page)
        search_settings.search_page = self.index
        search_settings.save()

        self.settings = IncidentFilterSettings.for_site(site)

        # Clear all settings in case some where created during
        # migrations.
        GeneralIncidentFilter.objects.filter(
            incident_filter_settings=self.settings,
        ).delete()

    def open_filters(self):
        self.browser.find_element_by_css_selector('.filters__button--summary-toggle').click()

    def apply_filters(self):
        self.browser.find_element_by_xpath('//button[@type="submit"][text()="Apply Filters"]').click()

    def add_general_filter(self, filter_name):
        GeneralIncidentFilter.objects.create(
            incident_filter=filter_name,
            incident_filter_settings=self.settings,
        )


@unittest.skip('Test applies to legacy templates')
class BooleanFilterTestCase(FilterTest):
    def setUp(self):
        super().setUp()

        self.category = CategoryPageFactory(
            parent=self.root_page,
            title='Leak Case',
            incident_filters=['charged_under_espionage_act'],
        )

        self.true_bool = IncidentPageFactory(
            categories=[self.category],
            charged_under_espionage_act=True
        )
        self.false_bool = IncidentPageFactory(
            categories=[self.category],
            charged_under_espionage_act=False
        )

    def test_filters_boolean_true(self):
        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()

        self.browser.find_element_by_css_selector('.filters__category').click()

        self.browser.find_element_by_xpath('//button[text()="Yes"]').click()

        self.apply_filters()

        url = urllib.parse.urlparse(self.browser.current_url)
        incidents = self.browser.find_elements_by_css_selector('article.incident')
        self.assertEqual(len(incidents), 1)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['charged_under_espionage_act'],
            ['True'],
        )

        self.open_filters()
        selected_button = self.browser.find_element_by_css_selector('button.radio-pill__item--selected')
        self.assertEqual(selected_button.text, 'Yes')

    def test_filters_boolean_false(self):
        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()

        self.browser.find_element_by_css_selector('.filters__category').click()

        self.browser.find_element_by_xpath('//button[text()="No"]').click()

        self.apply_filters()

        url = urllib.parse.urlparse(self.browser.current_url)
        incidents = self.browser.find_elements_by_css_selector('article.incident')
        self.assertEqual(len(incidents), 1)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['charged_under_espionage_act'],
            ['False'],
        )

        self.open_filters()
        selected_button = self.browser.find_element_by_css_selector('button.radio-pill__item--selected')
        self.assertEqual(selected_button.text, 'No')


class IntegerFilterTest(FilterTest):
    def setUp(self):
        super().setUp()

        self.add_general_filter('recently_updated')

        IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )

        incident_with_new_update = IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )
        IncidentUpdateFactory(
            page=incident_with_new_update,
            date=timezone.now() - timedelta(days=3),
        )

    def test_filters_integer(self):
        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()
        element = self.browser.find_element_by_css_selector('input.filter-int-input')
        element.send_keys('10')
        self.apply_filters()

        url = urllib.parse.urlparse(self.browser.current_url)
        incidents = self.browser.find_elements_by_css_selector('article.incident')
        self.assertEqual(len(incidents), 1)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['recently_updated'],
            ['10'],
        )

        self.open_filters()
        element = self.browser.find_element_by_css_selector('input.filter-int-input')
        self.assertEqual(element.get_attribute('value'), '10')


class MultiRelationFilterTest(FilterTest):
    def setUp(self):
        super().setUp()

        self.category = CategoryPageFactory(
            parent=self.root_page,
            title='Equipment Damage',
            incident_filters=['equipment_broken'],
        )

        self.equipment = [
            EquipmentFactory(name='Leather Armor'),
            EquipmentFactory(name='Scale Mail'),
            EquipmentFactory(name='Field Plate'),
        ]

        for equipment_set in powerset(self.equipment):
            incident = IncidentPageFactory(categories=[self.category])
            for equipment in equipment_set:
                EquipmentBrokenFactory(
                    incident=incident,
                    equipment=equipment,
                )
        self.browser.get(self.live_server_url + self.home_page.url)
        self.open_filters()
        self.browser.find_element_by_css_selector('.filters__category').click()
        self.autocomplete_input = self.browser.find_element_by_css_selector('.autocomplete__search')

    def test_filters_multiple_related_selections(self):
        wait = WebDriverWait(self.browser, 10)
        self.autocomplete_input.click()
        for equipment in self.equipment[:2]:
            wait.until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, f'//span[normalize-space(text()) = "{equipment.name}"]')
                )
            )
            self.browser.find_element_by_xpath(f'//span[normalize-space(text()) = "{equipment.name}"]').click()
            wait.until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, f'//span[text()="{equipment.name}"][@class="selection__label"]')
                )
            )
        self.apply_filters()

        url = urllib.parse.urlparse(self.browser.current_url)
        self.assertEqual(url.path, self.category.url)

        self.assertEqual(
            urllib.parse.parse_qs(url.query)['equipment_broken'],
            [f'{self.equipment[0].pk},{self.equipment[1].pk}'],
        )

        self.open_filters()

        self.assertEqual(
            {element.text for element in self.browser.find_elements_by_css_selector('.selection__label')},
            {equipment.name for equipment in self.equipment[:2]}
        )


class RelationFilterTest(FilterTest):
    def setUp(self):
        super().setUp()

        self.add_general_filter('state')

        State.objects.all().delete()
        self.vermont = StateFactory(name='Vermont')
        self.new_hampshire = StateFactory(name='New Hampshire')

        IncidentPageFactory(state=self.vermont)
        IncidentPageFactory(state=self.new_hampshire)

        self.browser.get(self.live_server_url + self.home_page.url)
        self.open_filters()
        self.autocomplete_input = self.browser.find_element_by_css_selector('.autocomplete__search')

    def test_filters_autocomplete_mouse_input(self):
        self.autocomplete_input.click()
        self.browser.find_element_by_xpath(f'//span[normalize-space(text()) = "{str(self.vermont)}"]').click()

        self.apply_filters()

        url = urllib.parse.urlparse(self.browser.current_url)
        self.assertEqual(url.path, self.index.url)

        self.assertEqual(
            urllib.parse.parse_qs(url.query)['state'],
            [str(self.vermont.pk)],
        )

        self.open_filters()
        self.assertEqual(
            {element.text for element in self.browser.find_elements_by_css_selector('.selection__label')},
            {str(self.vermont)}
        )

    def test_filters_autocomplete_keyboard_input(self):
        self.autocomplete_input.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(len(incidents), 1)
        self.assertEqual(url.path, self.index.url)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['state'],
            [str(self.new_hampshire.pk)],
        )

        self.open_filters()
        self.assertEqual(
            {element.text for element in self.browser.find_elements_by_css_selector('.selection__label')},
            {str(self.new_hampshire)}
        )


class SearchFilterTest(FilterTest):
    def setUp(self):
        super().setUp()

        IncidentPageFactory(title='Cuttlefish')
        self.browser.get(self.live_server_url + self.home_page.url)

    def test_filters_by_search(self):
        self.open_filters()
        element = self.browser.find_element_by_css_selector('input.filter-text-input')
        element.send_keys('Cuttlefish')

        self.apply_filters()

        url = urllib.parse.urlparse(self.browser.current_url)
        self.assertEqual(url.path, self.index.url)

        self.assertEqual(
            urllib.parse.parse_qs(url.query)['search'],
            ['Cuttlefish'],
        )

        self.open_filters()
        element = self.browser.find_element_by_css_selector('input.filter-text-input')
        self.assertEqual(element.get_attribute('value'), 'Cuttlefish')


class DateFilterTest(FilterTest):
    def setUp(self):
        super().setUp()

        self.add_general_filter('date')

        IncidentPageFactory(date='2020-02-15')
        IncidentPageFactory(date='2020-03-15')
        IncidentPageFactory(date='2020-04-15')

        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()
        self.lower, self.upper = self.browser.find_elements_by_css_selector('input.filter-date-picker')

    def test_filters_lower_date(self):
        self.lower.send_keys('04/01/2020')
        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        self.assertEqual(len(incidents), 1)

        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(
            urllib.parse.parse_qs(url.query)['date_lower'],
            ['2020-04-01'],
        )

        self.open_filters()
        lower, upper = self.browser.find_elements_by_css_selector('input.filter-date-picker')
        self.assertEqual(lower.get_attribute('value'), '04/01/2020')
        self.assertEqual(upper.get_attribute('value'), '')

    def test_filters_upper_date(self):
        self.upper.send_keys('04/01/2020')
        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        self.assertEqual(len(incidents), 2)

        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(
            urllib.parse.parse_qs(url.query)['date_upper'],
            ['2020-04-01'],
        )
        self.open_filters()
        lower, upper = self.browser.find_elements_by_css_selector('input.filter-date-picker')
        self.assertEqual(lower.get_attribute('value'), '')
        self.assertEqual(upper.get_attribute('value'), '04/01/2020')

    def test_filters_upper_and_lower_date(self):
        self.lower.send_keys('03/01/2020')
        self.upper.send_keys('04/01/2020')
        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        self.assertEqual(len(incidents), 1)

        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(
            urllib.parse.parse_qs(url.query)['date_upper'],
            ['2020-04-01'],
        )
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['date_lower'],
            ['2020-03-01'],
        )
        self.open_filters()
        lower, upper = self.browser.find_elements_by_css_selector('input.filter-date-picker')
        self.assertEqual(lower.get_attribute('value'), '03/01/2020')
        self.assertEqual(upper.get_attribute('value'), '04/01/2020')


class ChoiceFilterTest(FilterTest):
    def setUp(self):
        super().setUp()

        self.category = CategoryPageFactory(
            parent=self.root_page,
            title='Attack',
            incident_filters=['assailant', 'was_journalist_targeted'],
        )
        self.incidents = []
        for (boolean, actor) in itertools.product(choices.MAYBE_BOOLEAN, choices.ACTORS):
            self.incidents.append(
                IncidentPageFactory(
                    categories=[self.category],
                    assailant=actor[0],
                    was_journalist_targeted=boolean[0],
                )
            )

    def test_filters_by_maybe_boolean_choice_unknown(self):
        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()

        self.browser.find_element_by_css_selector('.filters__category').click()

        self.browser.find_element_by_xpath('//button[text()="Unknown"]').click()
        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(len(incidents), 6)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['was_journalist_targeted'],
            [choices.MAYBE_BOOLEAN[0][0]],
        )

        self.open_filters()
        selected_button = self.browser.find_element_by_css_selector('button.radio-pill__item--selected')
        self.assertEqual(selected_button.text, 'Unknown')

    def test_filters_by_maybe_boolean_choice_no(self):
        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()

        self.browser.find_element_by_css_selector('.filters__category').click()

        self.browser.find_element_by_xpath('//button[text()="No"]').click()
        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(len(incidents), 6)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['was_journalist_targeted'],
            [choices.MAYBE_BOOLEAN[2][0]],
        )
        self.open_filters()
        selected_button = self.browser.find_element_by_css_selector('button.radio-pill__item--selected')
        self.assertEqual(selected_button.text, 'No')

    def test_filters_by_dropdown_choice(self):
        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()
        self.browser.find_element_by_css_selector('.filters__category').click()

        select = Select(self.browser.find_element_by_css_selector('select.choice-input'))
        select.select_by_value(choices.ACTORS[1][0])

        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(len(incidents), 3)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['assailant'],
            [choices.ACTORS[1][0]],
        )

        self.open_filters()
        select = Select(self.browser.find_element_by_css_selector('select.choice-input'))

        self.assertEqual(
            {element.text for element in select.all_selected_options},
            {choices.ACTORS[1][1]}
        )

    def test_filters_by_multi_choice(self):
        self.browser.get(self.live_server_url + self.home_page.url)

        self.open_filters()
        self.browser.find_element_by_css_selector('.filters__category').click()

        select = Select(self.browser.find_element_by_css_selector('select.choice-input'))
        select.select_by_value(choices.ACTORS[2][0])
        self.browser.find_element_by_xpath('//button[text()="Yes"]').click()

        self.apply_filters()

        incidents = self.browser.find_elements_by_css_selector('article.incident')
        url = urllib.parse.urlparse(self.browser.current_url)

        self.assertEqual(len(incidents), 1)
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['assailant'],
            [choices.ACTORS[2][0]],
        )
        self.assertEqual(
            urllib.parse.parse_qs(url.query)['was_journalist_targeted'],
            [choices.MAYBE_BOOLEAN[1][0]],
        )

        self.open_filters()
        selected_button = self.browser.find_element_by_css_selector('button.radio-pill__item--selected')
        select = Select(self.browser.find_element_by_css_selector('select.choice-input'))

        self.assertEqual(selected_button.text, 'Yes')
        self.assertEqual(
            {element.text for element in select.all_selected_options},
            {choices.ACTORS[2][1]}
        )
