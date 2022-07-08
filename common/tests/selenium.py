import os
import socket
import unittest

from django.db import connections
from django.db.utils import OperationalError
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from wagtail.core.models import Page, Site, Locale


SELENIUM_HOST = os.environ['SELENIUM_HOST']
HOST_IP = socket.gethostbyname(socket.gethostname())


class SeleniumTest(StaticLiveServerTestCase):
    host = HOST_IP

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Remote(
            command_executor=f'http://{SELENIUM_HOST}:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

        # Workaround for https://code.djangoproject.com/ticket/22414
        # Persistent connections not closed by LiveServerTestCase, preventing dropping test databases
        # https://github.com/cjerdonek/django/commit/b07fbca02688a0f8eb159f0dde132e7498aa40cc
        def close_sessions(conn):
            close_sessions_query = """
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE
                    datname = current_database() AND
                    pid <> pg_backend_pid();
            """
            with conn.cursor() as cursor:
                try:
                    cursor.execute(close_sessions_query)
                except OperationalError:
                    # In case we terminate our own connection.
                    pass

        for alias in connections:
            connections[alias].close()
            close_sessions(connections[alias])

        super().tearDownClass()

    def populate_site(self):
        """Create basic site and page data that is expected to exist by
        wagtail but is removed during the database flush."""
        root = Page.objects.create(
            title='Root',
            path='0001',
            depth=1,
        )

        root_page = root.add_child(instance=Page(
            title='Home',
            path='00010001',
            depth=2,
        ))

        Site.objects.create(
            hostname=HOST_IP.rstrip(),
            port=80,
            is_default_site=True,
            root_page=root_page,
        )

    def setUp(self):
        super().setUp()

        Locale.objects.get_or_create(language_code='en')

        try:
            original_default_site = Site.objects.get(is_default_site=True, hostname='localhost')
            original_default_site.hostname = HOST_IP.rstrip()
            original_default_site.save()
        except Site.DoesNotExist:
            self.populate_site()

    def _fixture_teardown(self):
        # Allow TRUNCATE ... CASCADE and don't emit the post_migrate signal
        # when flushing only a subset of the apps
        # source:
        # https://github.com/wagtail/wagtail/issues/1824#issuecomment-467383062
        for db_name in self._databases_names(include_mirrors=False):
            # Flush the database
            inhibit_post_migrate = (
                self.available_apps is not None or
                (   # Inhibit the post_migrate signal when using serialized
                    # rollback to avoid trying to recreate the serialized data.
                    self.serialized_rollback and
                    hasattr(connections[db_name], '_test_serialized_contents')
                )
            )
            call_command('flush', verbosity=0, interactive=False,
                         database=db_name, reset_sequences=False,
                         allow_cascade=True,
                         inhibit_post_migrate=inhibit_post_migrate)
