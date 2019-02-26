import subprocess


def get_nginx_url():
    """
    Grab the relevant accessible URL to reach our prod django instance
    """
    return subprocess.check_output(['docker-compose',
                                    '-f',
                                    'prod-docker-compose.yaml',
                                    'port',
                                    'nginx',
                                    '8080']).rstrip().decode("utf-8")


def test_mainpage(host):
    """
    Basic test to make sure home-page is coming up.
    """
    SITE_STRING = "Press Freedom Incidents"

    URL = "http://{}".format(str(get_nginx_url()))

    content = host.check_output("curl -k {}".format(URL))
    head = host.check_output("curl -I -k {}".format(URL))
    assert SITE_STRING in content
    assert "HTTP/1.1 200 OK" in head
