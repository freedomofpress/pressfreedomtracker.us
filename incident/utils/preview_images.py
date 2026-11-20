import hashlib
import ipaddress
import socket
from html.parser import HTMLParser
from io import BytesIO
from urllib.parse import urljoin, urlsplit

from django.conf import settings
from django.core.cache import cache
from django.core.files.images import ImageFile

from wagtail.images import get_image_model
from wagtail.models import Collection

import PIL.Image
import requests
import structlog


logger = structlog.get_logger()

USER_AGENT = "PressFreedomTracker-LinkPreview/1.0 (+https://pressfreedomtracker.us)"
TIMEOUT = 5
MAX_PAGE_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 5
FAILURE_TTL = 60 * 60
COLLECTION_NAME = "External reporting previews"
IMAGE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}
IMAGE_KEYS = ("og:image", "og:image:secure_url", "twitter:image")
ALT_KEYS = ("og:image:alt", "twitter:image:alt")


class FetchError(Exception):
    pass


class _MetaImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attrs = dict(attrs)
        key = attrs.get("property") or attrs.get("name")
        if key in IMAGE_KEYS + ALT_KEYS and attrs.get("content"):
            self.found.setdefault(key, attrs["content"])


def find_preview_image_url_and_alt(html, base_url):
    parser = _MetaImageParser()
    parser.feed(html)
    found = parser.found
    url = next((found[key] for key in IMAGE_KEYS if key in found), None)
    alt = next((found[key] for key in ALT_KEYS if key in found), "")
    return (urljoin(base_url, url) if url else None), alt.strip()


def _check_public(url):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise FetchError(f"Unsupported URL {url!r}")
    try:
        addresses = socket.getaddrinfo(parts.hostname, None)
    except socket.gaierror as e:
        raise FetchError(f"Could not resolve {parts.hostname}") from e
    for *_, sockaddr in addresses:
        if not ipaddress.ip_address(sockaddr[0].split("%")[0]).is_global:
            raise FetchError(f"{parts.hostname} does not resolve to a public address")


def _get(url, max_bytes):
    # Redirects are followed by hand so every hop gets the public-address check.
    for _ in range(MAX_REDIRECTS + 1):
        _check_public(url)
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=False,
        )
        if response.is_redirect:
            response.close()
            url = urljoin(url, response.headers["Location"])
            continue
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_content(64 * 1024):
            content += chunk
            if len(content) > max_bytes:
                response.close()
                raise FetchError(f"{url} is larger than {max_bytes} bytes")
        return url, response, bytes(content)
    raise FetchError(f"Too many redirects from {url}")


def _get_collection():
    root = Collection.get_first_root_node()
    return root.get_children().filter(name=COLLECTION_NAME).first() or root.add_child(
        name=COLLECTION_NAME
    )


def _download(page_url, title, attribution):
    final_url, response, html = _get(page_url, MAX_PAGE_BYTES)
    html = html.decode(response.encoding or "utf-8", errors="replace")
    image_url, alt = find_preview_image_url_and_alt(html, final_url)
    if not image_url:
        raise FetchError(f"No preview image on {page_url}")

    _, response, data = _get(image_url, settings.WAGTAILIMAGES_MAX_UPLOAD_SIZE)
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    extension = IMAGE_EXTENSIONS.get(content_type)
    if not extension:
        raise FetchError(f"Unsupported image type {content_type!r} at {image_url}")

    with PIL.Image.open(BytesIO(data)) as pil_image:
        width, height = pil_image.size
    if width * height > settings.WAGTAILIMAGES_MAX_IMAGE_PIXELS:
        raise FetchError(f"{image_url} has too many pixels")

    image = get_image_model()(
        title=title[:255],
        description=alt[:255],
        attribution=attribution or None,
        slug=page_url[:1000],
        collection=_get_collection(),
        file=ImageFile(BytesIO(data), name=f"preview.{extension}"),
        file_size=len(data),
    )
    image.save()
    return image


def fetch_preview_image(page_url, title, attribution=""):
    """Return a stored copy of a page's Open Graph image, or None."""
    if existing := get_image_model().objects.filter(slug=page_url[:1000]).first():
        return existing

    failure_key = (
        "preview-image-failed:" + hashlib.sha256(page_url.encode()).hexdigest()
    )
    if cache.get(failure_key):
        return None

    try:
        return _download(page_url, title, attribution)
    except (
        FetchError,
        requests.RequestException,
        OSError,
        PIL.Image.DecompressionBombError,
    ) as e:
        logger.warning("Preview image fetch failed", url=page_url, error=str(e))
        cache.set(failure_key, True, FAILURE_TTL)
        return None
