import json
from collections.abc import Iterable

from wagtail.contrib.frontend_cache.backends import CloudflareBackend
from wagtail.contrib.frontend_cache.utils import get_backends

import requests
import structlog


__all__ = ["purge_all_from_cache", "purge_tags_from_cache"]


logger = structlog.get_logger("wagtail.frontendcache")


def for_every_cloudflare_backend(func: callable) -> callable:
    """Decorator to run a function once for every Cloudflare backend"""

    def inner(*args, backend_settings=None, backends=None, **kwargs):
        for backend in get_backends(
            backend_settings=backend_settings, backends=backends
        ).values():
            if not isinstance(backend, CloudflareBackend):
                continue
            func(*args, backend=backend, **kwargs)

    return inner


def purge(backend: CloudflareBackend, data=None) -> None:
    """Send a delete request to the Cloudflare API"""
    if data is None:
        data = {}
    purge_url = f"https://api.cloudflare.com/client/v4/zones/{backend.cloudflare_zoneid}/purge_cache"
    string_data = json.dumps(data)

    response = requests.delete(
        purge_url,
        json=data,
        headers={
            "X-Auth-Email": backend.cloudflare_email,
            "X-Auth-Key": backend.cloudflare_api_key,
            "Content-Type": "application/json",
        },
        timeout=5,
    )

    try:
        try:
            response_json = response.json()
        except ValueError:
            if response.status_code != 200:
                response.raise_for_status()
            else:
                logger.error(
                    "Couldn't purge from Cloudflare with data: %s. Unexpected JSON parse error.",
                    string_data,
                )  # pragma: no cover

    except requests.exceptions.HTTPError as e:
        logger.error(
            "Couldn't purge from Cloudflare with data: %s. HTTPError: %d %s",
            string_data,
            e.response.status_code,
            str(e),
        )
        return

    except requests.exceptions.InvalidURL as e:
        logger.error(
            "Couldn't purge from Cloudflare with data: %s. InvalidURL: %s",
            string_data,
            str(e),
        )
        return

    if response_json["success"] is False:
        error_messages = ", ".join(
            [str(err["message"]) for err in response_json["errors"]]
        )
        logger.error(
            "Couldn't purge from Cloudflare with data: %s. Cloudflare errors '%s'",
            string_data,
            error_messages,
        )
        return

    logger.info("Purged from CloudFlare with data: %s", string_data)


@for_every_cloudflare_backend
def purge_tags_from_cache(tags: Iterable, backend: CloudflareBackend) -> None:
    "Purge tags by list. Requires an enterprise Cloudflare subscription"
    purge(backend=backend, data={"tags": tags})


@for_every_cloudflare_backend
def purge_all_from_cache(backend: CloudflareBackend) -> None:
    "Purge an entire zone"
    purge(backend=backend)
