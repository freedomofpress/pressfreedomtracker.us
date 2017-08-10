import logging
import requests

from wagtail.contrib.wagtailfrontendcache import get_backends
from wagtail.contrib.wagtailfrontendcache.backends import CloudflareBackend


logger = logging.getLogger('wagtail.frontendcache')


def purge_tags_from_cache(tags, backend_settings=None, backends=None):
    for backend_name, backend in get_backends(backend_settings=backend_settings, backends=backends).items():

        if not isinstance(backend, CloudflareBackend):
            continue

        purge_url = 'https://api.cloudflare.com/client/v4/zones/{0}/purge_cache'.format(backend.cloudflare_zoneid)
        string_tags = ", ".join(tags)

        headers = {
            "X-Auth-Email": backend.cloudflare_email,
            "X-Auth-Key": backend.cloudflare_token,
            "Content-Type": "application/json",
        }

        data = {"tags": tags}

        response = requests.delete(
            purge_url,
            json=data,
            headers=headers,
        )

        try:
            response_json = response.json()
        except ValueError:
            if response.status_code != 200:
                response.raise_for_status()
            else:
                logger.error("Couldn't purge tags (%s) from Cloudflare. Unexpected JSON parse error.", string_tags)

        except requests.exceptions.HTTPError as e:
            logger.error("Couldn't purge tags (%s) from Cloudflare. HTTPError: %d %s", string_tags, e.response.status_code, e.message)
            continue

        except requests.exceptions.InvalidURL as e:
            logger.error("Couldn't purge tags (%s) from Cloudflare. URLError: %s", string_tags, e.message)
            continue

        if response_json['success'] is False:
            error_messages = ', '.join([str(err['message']) for err in response_json['errors']])
            logger.error("Couldn't purge tags (%s) from Cloudflare. Cloudflare errors '%s'", string_tags, error_messages)
            continue
