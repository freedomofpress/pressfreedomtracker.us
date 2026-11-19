import socket
from io import BytesIO
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings

import PIL.Image
import requests
from requests.structures import CaseInsensitiveDict

from incident.utils.preview_images import (
    COLLECTION_NAME,
    MAX_REDIRECTS,
    fetch_preview_image,
    find_preview_image_alt,
    find_preview_image_url,
)


ARTICLE_URL = "https://news.example/story"
IMAGE_URL = "https://news.example/lead.png"
ARTICLE_HTML = (
    b'<html><head><meta property="og:image" content="/lead.png">'
    b'<meta property="og:image:alt" content="A reporter outside city hall">'
    b"</head></html>"
)


def address(ip):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]


def png_bytes():
    buffer = BytesIO()
    PIL.Image.new("RGB", (4, 3)).save(buffer, "PNG")
    return buffer.getvalue()


def fake_response(url, content=b"", status=200, headers=None):
    response = requests.Response()
    response.url = url
    response.status_code = status
    response.headers = CaseInsensitiveDict(headers or {})
    response._content = content
    response._content_consumed = True
    response.encoding = "utf-8"
    return response


def article_and_image():
    return [
        fake_response(ARTICLE_URL, ARTICLE_HTML),
        fake_response(IMAGE_URL, png_bytes(), headers={"Content-Type": "image/png"}),
    ]


class FindPreviewImageUrlTestCase(SimpleTestCase):
    def test_prefers_og_image_and_resolves_relative_urls(self):
        html = (
            '<meta name="twitter:image" content="https://cdn.example/t.png">'
            '<meta property="og:image" content="/og.png">'
        )
        self.assertEqual(
            find_preview_image_url(html, "https://news.example/a/b"),
            "https://news.example/og.png",
        )

    def test_falls_back_to_twitter_image(self):
        html = '<meta name="twitter:image" content="https://cdn.example/t.png">'
        self.assertEqual(
            find_preview_image_url(html, ARTICLE_URL), "https://cdn.example/t.png"
        )

    def test_alt_prefers_og_and_falls_back_to_twitter(self):
        twitter = '<meta name="twitter:image:alt" content="From Twitter">'
        og = '<meta property="og:image:alt" content=" From Open Graph ">'
        self.assertEqual(find_preview_image_alt(twitter + og), "From Open Graph")
        self.assertEqual(find_preview_image_alt(twitter), "From Twitter")

    def test_alt_is_empty_when_missing(self):
        self.assertEqual(find_preview_image_alt("<title>Hi</title>"), "")

    def test_returns_none_without_preview_image(self):
        self.assertIsNone(find_preview_image_url("<title>Hi</title>", ARTICLE_URL))


@patch(
    "incident.utils.preview_images.socket.getaddrinfo",
    return_value=address("93.184.216.34"),
)
@patch("incident.utils.preview_images.requests.get")
class FetchPreviewImageTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_downloads_and_stores_image(self, get, getaddrinfo):
        get.side_effect = article_and_image()

        image = fetch_preview_image(ARTICLE_URL, "Story", "News Example")

        self.assertEqual((image.width, image.height), (4, 3))
        self.assertEqual(image.title, "Story")
        self.assertEqual(image.attribution, "News Example")
        self.assertEqual(image.description, "A reporter outside city hall")
        self.assertEqual(image.default_alt_text, "A reporter outside city hall")
        self.assertEqual(image.slug, ARTICLE_URL)
        self.assertEqual(image.collection.name, COLLECTION_NAME)
        self.assertEqual(get.call_args_list[1].args[0], IMAGE_URL)

    def test_reuses_stored_image_without_fetching(self, get, getaddrinfo):
        get.side_effect = article_and_image()
        first = fetch_preview_image(ARTICLE_URL, "Story")
        get.reset_mock()

        self.assertEqual(fetch_preview_image(ARTICLE_URL, "Story"), first)
        get.assert_not_called()

    def test_follows_redirects(self, get, getaddrinfo):
        get.side_effect = [
            fake_response(ARTICLE_URL, status=301, headers={"Location": "/moved"}),
            *article_and_image(),
        ]

        self.assertIsNotNone(fetch_preview_image(ARTICLE_URL, "Story"))
        self.assertEqual(get.call_args_list[1].args[0], "https://news.example/moved")

    def test_gives_up_after_too_many_redirects(self, get, getaddrinfo):
        get.return_value = fake_response(
            ARTICLE_URL, status=302, headers={"Location": ARTICLE_URL}
        )

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))
        self.assertEqual(get.call_count, MAX_REDIRECTS + 1)

    def test_refuses_private_addresses(self, get, getaddrinfo):
        getaddrinfo.return_value = address("10.0.0.1")

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))
        get.assert_not_called()

    def test_refuses_unresolvable_hosts(self, get, getaddrinfo):
        getaddrinfo.side_effect = socket.gaierror

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))
        get.assert_not_called()

    def test_refuses_non_http_urls(self, get, getaddrinfo):
        self.assertIsNone(fetch_preview_image("ftp://news.example/story", "Story"))
        get.assert_not_called()

    def test_remembers_failures(self, get, getaddrinfo):
        get.return_value = fake_response(ARTICLE_URL, b"<title>No preview</title>")
        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))
        get.reset_mock()

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))
        get.assert_not_called()

    def test_refuses_non_image_responses(self, get, getaddrinfo):
        get.side_effect = [
            fake_response(ARTICLE_URL, ARTICLE_HTML),
            fake_response(IMAGE_URL, b"<html>", headers={"Content-Type": "text/html"}),
        ]

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))

    @patch("incident.utils.preview_images.MAX_PAGE_BYTES", 10)
    def test_refuses_oversized_pages(self, get, getaddrinfo):
        get.return_value = fake_response(ARTICLE_URL, ARTICLE_HTML)

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))

    @override_settings(WAGTAILIMAGES_MAX_IMAGE_PIXELS=10)
    def test_refuses_images_with_too_many_pixels(self, get, getaddrinfo):
        get.side_effect = article_and_image()

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))

    def test_handles_request_errors(self, get, getaddrinfo):
        get.side_effect = requests.ConnectionError

        self.assertIsNone(fetch_preview_image(ARTICLE_URL, "Story"))
