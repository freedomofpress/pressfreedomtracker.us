from wagtail.core.models import Page
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from common.tests.selenium import SeleniumTest
from incident.tests.factories import IncidentIndexPageFactory, IncidentPageFactory


class PaginationTestCase(SeleniumTest):
    def setUp(self):
        super().setUp()
        root_page = Page.objects.get(slug='home')

        self.index = IncidentIndexPageFactory(parent=root_page)

        IncidentPageFactory.create_batch(30, parent=self.index)

    def test_next_page_button(self):
        more_css = '.js-incident-loading-next-link'
        incident_css = 'article.incident'
        incidents_per_page = 8

        self.browser.get(self.live_server_url + self.index.url)

        incidents = self.browser.find_elements_by_css_selector(incident_css)
        expected_incidents = incidents_per_page
        self.assertEqual(len(incidents), expected_incidents)

        self.browser.find_element_by_css_selector(more_css).click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(expected_conditions.url_contains('?endpage=2'))
        incidents = self.browser.find_elements_by_css_selector(incident_css)
        expected_incidents += incidents_per_page
        self.assertEqual(len(incidents), expected_incidents)

        self.browser.find_element_by_css_selector(more_css).click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(expected_conditions.url_contains('?endpage=3'))
        incidents = self.browser.find_elements_by_css_selector(incident_css)
        expected_incidents += incidents_per_page
        self.assertEqual(len(incidents), expected_incidents)
