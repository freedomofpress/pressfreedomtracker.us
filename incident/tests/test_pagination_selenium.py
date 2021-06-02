from wagtail.core.models import Page
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from common.tests.selenium import SeleniumTest
from incident.tests.factories import IncidentIndexPageFactory, IncidentPageFactory


class element_has_href(object):
    """An expectation for checking that an element has a particular href value.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, locator, css_class):
        self.locator = locator
        self.css_class = css_class

    def __call__(self, driver):
        element = driver.find_element(*self.locator)   # Finding the referenced element
        if self.css_class in element.get_attribute("href"):
            return element
        else:
            return False


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
        wait.until(element_has_href((By.CSS_SELECTOR, more_css), "?page=3"))
        incidents = self.browser.find_elements_by_css_selector(incident_css)
        expected_incidents += incidents_per_page
        self.assertEqual(len(incidents), expected_incidents)

        self.browser.find_element_by_css_selector(more_css).click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(element_has_href((By.CSS_SELECTOR, more_css), "?page=4"))
        incidents = self.browser.find_elements_by_css_selector(incident_css)
        expected_incidents += incidents_per_page
        self.assertEqual(len(incidents), expected_incidents)
