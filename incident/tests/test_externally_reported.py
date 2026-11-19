from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase

from wagtail.models import Site
from wagtail.rich_text import RichText
from wagtail.test.utils.form_data import (
    inline_formset,
    nested_form_data,
    rich_text,
    streamfield,
)

import wagtail_factories

from common.models import SiteSettings, SocialSharingSEOSettings
from common.tests.factories import CategoryPageFactory, CustomImageFactory
from incident.models import ExternalReport
from incident.models.incident_page import IncidentPage

from .factories import (
    ExternalReportFactory,
    IncidentIndexPageFactory,
    IncidentPageFactory,
)


def make_document():
    return wagtail_factories.DocumentFactory(
        title="Cease and desist letter",
        file__from_file=ContentFile(b"%PDF-1.4", name="letter.pdf"),
    )


class IncidentPageFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.index = IncidentIndexPageFactory(parent=site.root_page)
        cls.category = CategoryPageFactory(parent=site.root_page)
        cls.user = get_user_model().objects.create_superuser(
            username="editor", email="editor@example.com", password="password"
        )

    def make_form(self, externally_reported, body=None, external_reports=None):
        data = nested_form_data(
            {
                "title": "An incident",
                "slug": "an-incident",
                "date": "2025-06-08",
                "externally_reported": "on" if externally_reported else "",
                "body": streamfield(body or []),
                "state": "null",
                "targeted_institutions": "null",
                "targeted_journalists": inline_formset([]),
                "tags": "null",
                "charges": inline_formset([]),
                "legal_orders": inline_formset([]),
                "arresting_authority": "null",
                "target_nationality": "null",
                "workers_whose_communications_were_obtained": "null",
                "politicians_or_public_figures_involved": "null",
                "related_incidents": "null",
                "updates": inline_formset([]),
                "external_reports": inline_formset(external_reports or []),
                "categories": inline_formset([{"category": str(self.category.pk)}]),
                "authors": inline_formset([]),
                "equipment_seized": inline_formset([]),
                "equipment_broken": inline_formset([]),
            }
        )
        form_class = IncidentPage.get_edit_handler().get_form_class()
        return form_class(
            data,
            instance=IncidentPage(),
            for_user=self.user,
            parent_page=self.index,
        )

    def test_full_incident_requires_body(self):
        form = self.make_form(externally_reported=False)
        self.assertFalse(form.is_valid())
        self.assertIn("body", form.errors)

    def test_full_incident_with_body_is_valid(self):
        form = self.make_form(
            externally_reported=False,
            body=[("rich_text", rich_text("<p>Our write-up</p>"))],
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_externally_reported_incident_does_not_require_body(self):
        form = self.make_form(
            externally_reported=True,
            external_reports=[
                {"title": "Editorial", "url": "https://example.com/editorial"}
            ],
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_externally_reported_incident_accepts_a_document(self):
        document = make_document()
        form = self.make_form(
            externally_reported=True,
            external_reports=[{"title": "Letter", "document": str(document.pk)}],
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_externally_reported_incident_requires_an_external_report(self):
        form = self.make_form(externally_reported=True)
        self.assertFalse(form.is_valid())
        self.assertIn("externally_reported", form.errors)

    def test_deleted_external_report_does_not_count(self):
        form = self.make_form(
            externally_reported=True,
            external_reports=[
                {
                    "title": "Editorial",
                    "url": "https://example.com/editorial",
                    "DELETE": "1",
                }
            ],
        )
        self.assertFalse(form.is_valid())
        self.assertIn("externally_reported", form.errors)

    def test_draft_save_skips_body_and_external_report_requirements(self):
        for externally_reported in (True, False):
            with self.subTest(externally_reported=externally_reported):
                form = self.make_form(externally_reported=externally_reported)
                form.defer_required_fields()
                self.assertTrue(form.is_valid(), form.errors)


class ExternalReportTestCase(TestCase):
    def test_requires_url_or_document(self):
        with self.assertRaisesMessage(ValidationError, "Add a URL or a document."):
            ExternalReport(title="Nothing").clean()

    def test_rejects_both_url_and_document(self):
        report = ExternalReport(
            title="Both", url="https://example.com", document=make_document()
        )
        with self.assertRaisesMessage(ValidationError, "not both"):
            report.clean()

    def test_href_uses_document_url(self):
        document = make_document()
        report = ExternalReport(title="Letter", document=document)
        self.assertEqual(report.href, document.url)

    def test_str_includes_href_and_publication(self):
        report = ExternalReport(
            title="Editorial", url="https://example.com", publication="Sentinel"
        )
        self.assertEqual(str(report), "Editorial (https://example.com) via Sentinel")

    def test_str_without_href(self):
        self.assertEqual(str(ExternalReport(title="Gone")), "Gone")


class ExternallyReportedDisplayTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.index = IncidentIndexPageFactory(parent=site.root_page)
        cls.stub = IncidentPageFactory(parent=cls.index, externally_reported=True)
        ExternalReportFactory(
            page=cls.stub,
            title="Intimidation won't make the Sentinel back down",
            url="https://example.com/sentinel-editorial",
            publication="Orlando Sentinel",
            preview_text="The Sentinel will keep reporting on Hope Florida.",
        )
        cls.document = make_document()
        ExternalReportFactory(
            page=cls.stub,
            title="Cease and desist",
            publication="Florida DCF",
            url="",
            document=cls.document,
        )
        cls.full = IncidentPageFactory(parent=cls.index)

    def test_stub_page_shows_external_reports(self):
        response = self.client.get(self.stub.url)
        self.assertContains(response, "external-reports")
        self.assertContains(response, "https://example.com/sentinel-editorial")
        self.assertContains(response, "Orlando Sentinel")
        self.assertContains(response, self.document.url)
        self.assertContains(
            response, "The Sentinel will keep reporting on Hope Florida."
        )
        self.assertContains(response, "PDF (8\xa0bytes)")

    def test_document_full_url_is_absolute(self):
        report = self.stub.external_reports.get(document=self.document)
        self.assertEqual(
            report.get_full_url(),
            urljoin(self.stub.get_full_url(), self.document.url),
        )
        self.assertTrue(report.get_full_url().startswith("http"))

    def test_meta_line_separator_is_surrounded_by_spaces(self):
        response = self.client.get(self.stub.url)
        self.assertContains(
            response,
            'Florida DCF <span class="external-reports__separator" aria-hidden="true">&bull;</span> PDF',
        )

    def test_stub_page_shows_report_image(self):
        ExternalReportFactory(page=self.stub, image=CustomImageFactory())
        response = self.client.get(self.stub.url)
        self.assertContains(response, "external-reports__image")

    def test_stub_page_shows_default_heading(self):
        response = self.client.get(self.stub.url)
        self.assertContains(response, ">Externally reported</h3>")

    def test_stub_page_shows_editable_heading(self):
        settings = SiteSettings.for_site(Site.objects.get(is_default_site=True))
        settings.externally_reported_heading = "Reported elsewhere"
        settings.save()
        response = self.client.get(self.stub.url)
        self.assertContains(response, ">Reported elsewhere</h3>")

    def test_stub_page_shows_editable_note(self):
        settings = SiteSettings.for_site(Site.objects.get(is_default_site=True))
        settings.externally_reported_note = "<p>Verified by our reporters.</p>"
        settings.save()
        response = self.client.get(self.stub.url)
        self.assertContains(response, "Verified by our reporters.")

    def test_full_incident_page_has_no_external_reporting(self):
        response = self.client.get(self.full.url)
        self.assertNotContains(response, "external-reports")

    def test_incident_without_body_omits_date_anchor(self):
        response = self.client.get(self.stub.url)
        self.assertNotContains(response, "incident-original")

    def test_incident_with_body_shows_date_anchor(self):
        self.full.body = [("rich_text", RichText("<p>Our write-up</p>"))]
        self.full.save()
        response = self.client.get(self.full.url)
        self.assertContains(response, "incident-original")

    def test_meta_description_falls_back_to_site_default(self):
        settings = SocialSharingSEOSettings.for_site(
            Site.objects.get(is_default_site=True)
        )
        settings.default_description = "Tracking press freedom violations."
        settings.save()
        self.assertEqual(
            self.stub.get_meta_description(), "Tracking press freedom violations."
        )

    def test_meta_description_is_empty_without_site_default(self):
        self.assertEqual(self.stub.get_meta_description(), "")
