from unittest import mock

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse


import wagtail.blocks
from wagtail.models import Site

import defusedxml.ElementTree as ET

from blog.models import BlogIndexPageFeature
from blog.wagtail_hooks import register_permissions
from common.exceptions import ChartNotAvailable
from common.models.charts import ChartSnapshot
from common.tests.factories import (
    CategoryPageFactory,
    CustomImageFactory,
    OrganizationPageFactory,
    PersonPageFactory,
)
from incident.tests.factories import IncidentPageFactory

from .factories import BlogIndexPageFactory, BlogPageFactory


class TestPages(TestCase):
    """Incident Index Page"""

    @classmethod
    def setUpTestData(cls):
        # Get default site
        site = Site.objects.get(is_default_site=True)

        # Get the root home page
        cls.home_page = site.root_page

        CustomImageFactory.create(
            file__width=800,
            file__height=600,
            file__color="green",
            collection__name="Photos",
        )

        cls.search_image = CustomImageFactory.create(
            file__width=333,
            file__height=444,
            file__color="orange",
            collection__name="Photos",
        )

        cls.index = BlogIndexPageFactory(parent=site.root_page, slug="all-blogs")
        cls.blog_page = BlogPageFactory(
            parent=cls.index,
            slug="one",
            with_image=True,
        )
        cls.blog_page2 = BlogPageFactory(
            parent=cls.index,
            slug="two",
            with_teaser_chart=True,
            search_image=cls.search_image,
        )
        cls.blog_page3 = BlogPageFactory(
            parent=cls.index,
            slug="three",
        )
        cat = CategoryPageFactory()
        IncidentPageFactory(categories=[cat])

    def setUp(self):
        self.client = Client()

    def test_get_index_should_succeed(self):
        """get index should succed."""
        response = self.client.get("/all-blogs/")
        self.assertEqual(response.status_code, 200)

    def test_get_index_feed_should_succeed(self):
        """get feed should succed."""
        response = self.client.get(self.index.url + "feed/")
        self.assertEqual(response["content-type"], "application/rss+xml; charset=utf-8")
        self.assertEqual(response.status_code, 200)

    def test_rss_feed_has_correct_thumbnails(self):
        response = self.client.get(self.index.url + "feed/")
        root = ET.fromstring(response.content)

        namespaces = {"media": "http://search.yahoo.com/mrss/"}
        item1 = root.find(f".//item[title='{self.blog_page.title}']")
        item2 = root.find(f".//item[title='{self.blog_page2.title}']")

        self.assertIn(
            self.blog_page.teaser_graphic[0].value.get_rendition("original").url,
            getattr(
                item1.find(
                    "media:thumbnail",
                    namespaces=namespaces,
                ),
                "attrib",
                {},
            ).get("url"),
        )

        expected_chart_thumbnail = self.blog_page2.teaser_graphic[
            0
        ].value.svg_snapshot_mini_datauri()
        self.assertIn(
            expected_chart_thumbnail,
            getattr(
                item2.find(
                    "media:thumbnail",
                    namespaces=namespaces,
                ),
                "attrib",
                {},
            ).get("url"),
        )

    def test_rss_feed_has_correct_if_chart_not_available(self):
        with mock.patch.object(ChartSnapshot, "get_or_generate") as get_or_generate:
            get_or_generate.side_effect = ChartNotAvailable
            response = self.client.get(self.index.url + "feed/")
        root = ET.fromstring(response.content)

        namespaces = {"media": "http://search.yahoo.com/mrss/"}
        item1 = root.find(f".//item[title='{self.blog_page.title}']")
        item2 = root.find(f".//item[title='{self.blog_page2.title}']")

        self.assertIn(
            self.blog_page.teaser_graphic[0].value.get_rendition("original").url,
            getattr(
                item1.find(
                    "media:thumbnail",
                    namespaces=namespaces,
                ),
                "attrib",
                {},
            ).get("url"),
        )

        self.assertIn(
            # The search image is used as a fallback if the chart
            # snapshot not available.
            self.blog_page2.search_image.get_rendition("original").url,
            getattr(
                item2.find(
                    "media:thumbnail",
                    namespaces=namespaces,
                ),
                "attrib",
                {},
            ).get("url"),
        )

    def test_get_index_for_unknown_author_should_return_404(self):
        response = self.client.get("/all-blogs/?author=999")
        self.assertEqual(response.status_code, 404)

    def test_get_index_for_author_should_return_author_title_in_response(self):
        author = PersonPageFactory(title="A Person")
        response = self.client.get(f"/all-blogs/?author={author.pk}")
        self.assertContains(response, author.title)

    def test_get_person_page_does_not_raise_error(self):
        author = PersonPageFactory(title="A Person", parent=self.index)
        response = self.client.get(author.get_url())
        self.assertRedirects(response, self.index.get_url() + f"?author={author.pk}")

    def test_person_pages_not_in_sitemap(self):
        author = PersonPageFactory(title="A Person", parent=self.index)
        response = self.client.get(reverse("sitemap"))
        author_url = author.get_url()
        self.assertNotContains(response, author_url)

    def test_get_author_raises_404_if_no_index(self):
        author = PersonPageFactory(title="A Person", parent=self.home_page)
        self.index.delete()
        response = self.client.get(author.get_url())
        self.assertEqual(response.status_code, 404)

    def test_get_index_for_author_should_not_contain_featured_blogs(self):
        BlogIndexPageFeature.objects.create(
            blog_index_page=self.index,
            page=self.blog_page,
        )
        author = PersonPageFactory()
        response = self.client.get(f"/all-blogs/?author={author.pk}")
        self.assertNotContains(response, "Featured")

    def test_get_index_for_unknown_organization_should_return_404(self):
        response = self.client.get("/all-blogs/?organization=999")
        self.assertEqual(response.status_code, 404)

    def test_get_index_for_organization_should_return_organization_title_in_response(
        self,
    ):
        org = OrganizationPageFactory(title="An Organization")
        response = self.client.get(f"/all-blogs/?organization={org.pk}")
        self.assertContains(response, org.title)

    def test_get_index_for_organization_should_not_contain_featured_blogs(self):
        BlogIndexPageFeature.objects.create(
            blog_index_page=self.index,
            page=self.blog_page,
        )
        org = OrganizationPageFactory()
        response = self.client.get(f"/all-blogs/?organization={org.pk}")
        self.assertNotContains(response, "Featured")

    def test_get_blog_page_contains_lead_graphic_image_attribution(self):
        image = CustomImageFactory()
        self.blog_page.lead_graphic = wagtail.blocks.StreamValue(
            stream_block=self.blog_page.lead_graphic.stream_block,
            stream_data=[("image", image)],
        )
        self.blog_page.save()
        expected_attribution = image.attribution
        response = self.client.get(self.blog_page.url)
        self.assertContains(
            response,
            f'<span class="media-attribution"> — {expected_attribution}</span>',
            html=True,
        )

    def test_get_blog_page_vertical_bar_chart_additional_js_media(self):
        response = self.client.get(self.blog_page.url)
        self.assertContains(response, "verticalBarChart")

        # Remove the bar chart from the body and the lead graphic --
        # not sure if there's an easier way to ensure this!
        new_body = []
        for item in self.blog_page.body:
            if item.block_type == "vertical_bar_chart":
                continue
            new_body.append((item.block_type, item.value))
        self.blog_page.body = new_body
        self.blog_page.lead_graphic = None
        self.blog_page.save()

        # We should no longer have that JS bundle in the response
        response = self.client.get(self.blog_page.url)
        self.assertNotContains(response, "verticalBarChart")

    def test_get_blog_page_base_url(self):
        self.assertEqual(
            self.blog_page2.get_base_url(), self.home_page.get_site().root_url
        )

    def test_get_blog_page_newsletter_preamble(self):
        self.index.newsletter_preamble = "Test preamble"
        self.index.save()
        self.assertEqual(
            self.blog_page.get_newsletter_preamble(),
            "Test preamble",
        )

        self.blog_page.newsletter_preamble = "Preamble override"
        self.blog_page.save()
        self.assertEqual(
            self.blog_page.get_newsletter_preamble(),
            "Preamble override",
        )

    def test_newsletter_preview_text_uses_preamble_as_plain_text(self):
        # The preheader teaser comes from the preamble, with rich-text HTML
        # stripped and entities decoded so the template doesn't double-encode.
        self.blog_page.newsletter_preamble = "<p>Intro <b>teaser</b> &amp; more.</p>"
        self.blog_page.save()
        self.assertEqual(
            self.blog_page.get_newsletter_preview_text(),
            "Intro teaser & more.",
        )

    def test_newsletter_preview_text_falls_back_to_first_text_block(self):
        # With no preamble on the page or its index, the teaser falls back to
        # the first text block, skipping non-text blocks.
        page = BlogPageFactory(parent=self.index, slug="preview-fallback")
        page.newsletter_preamble = None
        page.body = [
            ("raw_html", "<div>ignore me</div>"),
            ("text", {"text": "<p>First body paragraph.</p>"}),
        ]
        page.save()
        self.index.newsletter_preamble = None
        self.index.save()
        self.assertEqual(
            page.get_newsletter_preview_text(),
            "First body paragraph.",
        )

    def test_newsletter_renders_without_preamble(self):
        # Regression: a newsletter page with a lead graphic but no preamble
        # set on either the page or its index page must still render. The
        # intro section is emitted because of the lead graphic, and
        # get_newsletter_preamble() returns None in that case -- passing None
        # to the newsletter_richtext filter used to raise ValueError.
        image = CustomImageFactory.create(
            file__width=600,
            file__height=400,
            collection__name="Photos",
        )
        page = BlogPageFactory(parent=self.index, slug="no-preamble")
        page.newsletter_preamble = None
        page.body = []
        page.lead_graphic = [("image", image)]
        page.save()
        self.index.newsletter_preamble = None
        self.index.save()

        self.assertIsNone(page.get_newsletter_preamble())
        html = page.get_newsletter_html()
        self.assertIn("Submit an incident", html)

    def test_newsletter_links_back_to_the_post(self):
        html = self.blog_page3.get_newsletter_html()
        self.assertIn("View this newsletter on pressfreedomtracker.us", html)
        self.assertIn(self.blog_page3.full_url, html)

    def test_newsletter_web_link_can_be_hidden(self):
        self.blog_page3.hide_newsletter_web_link = True
        self.blog_page3.save()
        html = self.blog_page3.get_newsletter_html()
        self.assertNotIn("View this newsletter on pressfreedomtracker.us", html)

    def test_get_blog_page_vertical_bar_chart_meta_image(self):
        self.assertEqual(
            self.blog_page2.get_meta_image(),
            self.blog_page2.teaser_graphic[0].value.png_snapshot_meta(),
        )

    @mock.patch.object(ChartSnapshot, "get_or_generate")
    def test_get_blog_page_vertical_bar_chart_meta_image_if_pregeneration_fails(
        self,
        mock_snapshot,
    ):
        mock_snapshot.side_effect = ChartNotAvailable
        self.assertEqual(
            self.blog_page2.get_meta_image(),
            self.search_image,
        )

    def test_get_blog_page_normal_meta_image(self):
        self.assertEqual(
            self.blog_page.get_meta_image(), self.blog_page.teaser_graphic[0].value
        )

    def test_get_blog_page_absent_meta_image(self):
        self.assertIsNone(self.blog_page3.get_meta_image())

    def test_simple_summary(self):
        author = PersonPageFactory(title="A Person")
        blog_page = BlogPageFactory(
            parent=self.index,
            authors=[author],
        )
        self.assertEqual(blog_page.authors.first().summary, "A Person")


class TestBlogPageNewsletterPermission(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Get default site
        site = Site.objects.get(is_default_site=True)

        cls.index = BlogIndexPageFactory(parent=site.root_page, slug="all-blogs")
        cls.blog_page = BlogPageFactory(parent=cls.index, slug="blog")

        cls.user_with_perm = User.objects.create_user("user_with_perm", password="pass")
        content_type = ContentType.objects.get_for_model(cls.blog_page)
        perm = Permission.objects.get(
            content_type=content_type,
            codename="access_newsletter_tab_blogpage",
        )
        cls.user_with_perm.user_permissions.add(perm)

        cls.user_without_perm = User.objects.create_user(
            "user_without_perm", password="pass"
        )

    def test_has_newsletter_permission_returns_true_for_user_with_permission(self):
        user = User.objects.get(pk=self.user_with_perm.pk)
        self.assertTrue(
            self.blog_page.has_newsletter_permission(user, "access_newsletter_tab")
        )

    def test_has_newsletter_permission_returns_false_for_user_without_permission(self):
        self.assertFalse(
            self.blog_page.has_newsletter_permission(
                self.user_without_perm, "access_newsletter_tab"
            )
        )


class TestRegisterPermissionsHook(TestCase):
    def test_register_permissions_returns_blog_permissions(self):
        codenames = list(register_permissions().values_list("codename", flat=True))
        self.assertIn("access_newsletter_tab_blogpage", codenames)
