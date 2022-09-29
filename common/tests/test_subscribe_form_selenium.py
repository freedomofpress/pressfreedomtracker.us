from unittest import mock

from wagtail.core.models import Page, Site
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

from emails.models import Subscription
from common.tests.selenium import SeleniumTest
from common.tests.factories import SimplePageFactory
from emails.devdata import EmailSettingsFactory
from common.utils import MailchimpError


class SubscribeFormNoJSTestCase(SeleniumTest):
    javascript_enabled = False

    def setUp(self):
        super().setUp()
        root_page = Page.objects.get(slug='home')
        self.site = Site.objects.get()
        EmailSettingsFactory(site=self.site)
        self.page = SimplePageFactory(parent=root_page)

    @mock.patch('common.views.subscribe_for_site')
    def test_form_submission(self, mock_subscribe):
        full_name = 'Treebeard'
        email = 'treebeard@example.com'
        self.browser.get(self.live_server_url + self.page.url)
        name_input = self.browser.find_element(By.ID, 'mce-MMERGE6')
        email_input = self.browser.find_element(By.ID, 'mce-EMAIL')

        handles = self.browser.window_handles
        name_input.send_keys(full_name)
        email_input.send_keys(email)
        email_input.submit()
        WebDriverWait(self.browser, 10).until(
            expected_conditions.new_window_is_opened(handles)
        )
        self.browser.switch_to.window(self.browser.window_handles[-1])
        header = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        self.assertEqual(header.text, 'Thank you for subscribing!')
        mock_subscribe.assert_called_once_with(
            self.site,
            Subscription(email=email, full_name=full_name)
        )

    @mock.patch('common.views.subscribe_for_site')
    def test_form_submission_error(self, mock_subscribe):
        mock_subscribe.side_effect = MailchimpError

        full_name = 'Treebeard'
        email = 'treebeard@example.com'
        self.browser.get(self.live_server_url + self.page.url)
        name_input = self.browser.find_element(By.ID, 'mce-MMERGE6')
        email_input = self.browser.find_element(By.ID, 'mce-EMAIL')

        handles = self.browser.window_handles
        name_input.send_keys(full_name)
        email_input.send_keys(email)
        email_input.submit()
        WebDriverWait(self.browser, 10).until(
            expected_conditions.new_window_is_opened(handles)
        )
        self.browser.switch_to.window(self.browser.window_handles[-1])
        header = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        self.assertEqual(header.text, 'Subscription Error')
        WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//p[normalize-space()='An internal error occurred']")
            )
        )


class SubscribeFormJSTestCase(SeleniumTest):
    javascript_enabled = True

    def setUp(self):
        super().setUp()
        root_page = Page.objects.get(slug='home')
        self.site = Site.objects.get()
        EmailSettingsFactory(site=self.site)
        self.page = SimplePageFactory(parent=root_page)

    @mock.patch('common.views.subscribe_for_site')
    def test_form_submission(self, mock_subscribe):
        full_name = 'Treebeard'
        email = 'treebeard@example.com'
        self.browser.get(self.live_server_url + self.page.url)
        name_input = self.browser.find_element(By.ID, 'mce-MMERGE6')
        email_input = self.browser.find_element(By.ID, 'mce-EMAIL')
        name_input.send_keys(full_name)
        email_input.send_keys(email)
        email_input.submit()

        element = WebDriverWait(self.browser, 10).until(
            expected_conditions.visibility_of_element_located((By.ID, "mc-subscribe-thanks"))
        )
        self.assertIn(
            "Thanks for subscribing to Freedom of the Press Foundation",
            element.text,
        )
        mock_subscribe.assert_called_once_with(
            self.site,
            Subscription(email=email, full_name=full_name)
        )

    @mock.patch('common.views.subscribe_for_site')
    def test_form_submission_error(self, mock_subscribe):
        mock_subscribe.side_effect = MailchimpError

        full_name = 'Treebeard'
        email = 'treebeard@example.com'
        self.browser.get(self.live_server_url + self.page.url)
        name_input = self.browser.find_element(By.ID, 'mce-MMERGE6')
        email_input = self.browser.find_element(By.ID, 'mce-EMAIL')
        name_input.send_keys(full_name)
        email_input.send_keys(email)
        email_input.submit()

        element = WebDriverWait(self.browser, 10).until(
            expected_conditions.visibility_of_element_located((By.ID, "mce-error-response"))
        )
        self.assertEqual(
            element.text,
            'An internal error occurred.',
        )


class SubscribeFormJSNoNameTestCase(SeleniumTest):
    javascript_enabled = True

    def setUp(self):
        super().setUp()
        root_page = Page.objects.get(slug='home')
        self.site = Site.objects.get()
        EmailSettingsFactory(
            site=self.site,
            mailchimp_collect_name=False,
        )
        self.page = SimplePageFactory(parent=root_page)

    @mock.patch('common.views.subscribe_for_site')
    def test_form_submission(self, mock_subscribe):
        email = 'treebeard@example.com'
        self.browser.get(self.live_server_url + self.page.url)
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.ID, 'mce-MMERGE6')
        email_input = self.browser.find_element(By.ID, 'mce-EMAIL')
        email_input.send_keys(email)
        email_input.submit()

        element = WebDriverWait(self.browser, 10).until(
            expected_conditions.visibility_of_element_located((By.ID, "mc-subscribe-thanks"))
        )
        self.assertIn(
            "Thanks for subscribing to Freedom of the Press Foundation",
            element.text,
        )
        mock_subscribe.assert_called_once_with(
            self.site,
            Subscription(email=email, full_name=None)
        )
