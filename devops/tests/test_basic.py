import ssl
import os
import urllib2 as urllib

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_mainpage(Command):
    """
    Basic test to make sure home-page is coming up.
    """
    SITE_STRING = "Press Freedom Incidents"

    # When running under CI, the docker environment is remote and ports are
    # readily accessible remotely. In that case poll from the docker image
    # instead of from the host
    if os.environ.get("CIRCLECI", "false") != "true":
        # Disable SSL verification - we are using self-signed certs here people!
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        request = urllib.urlopen('https://localhost:4443', context=context)
        assert request.getcode() == 200
        assert SITE_STRING in str(request.read())
    else:
        content = Command.check_output("curl -k https://localhost:443")
        head = Command.check_output("curl -I -k https://localhost:443")
        assert "Press Freedom Incidents" in content
        assert "HTTP/1.1 200 OK" in head
