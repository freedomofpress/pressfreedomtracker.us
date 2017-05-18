import ssl
import urllib2 as urllib


def test_mainpage():
    """
    Basic test to make sure home-page is coming up.
    """
    # Disable SSL verification - we are using self-signed certs here people!
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    request = urllib.urlopen('https://localhost:4443', context=context)

    assert request.getcode() == 200
    assert "Press Freedom Incidents" in str(request.read())
