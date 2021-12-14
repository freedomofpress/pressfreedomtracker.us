import subprocess
import pytest


@pytest.mark.skip(reason="Skipping till templates have been added")
def test_mainpage(host):
    """
    Basic test to make sure home-page is coming up.
    """
    SITE_STRING = "Press Freedom Tracker"

    URL = "http://localhost:8000"

    content = host.check_output("curl -k {}".format(URL))
    head = host.check_output("curl -I -k {}".format(URL))
    assert SITE_STRING in content
    assert "HTTP/1.1 200 OK" in head
