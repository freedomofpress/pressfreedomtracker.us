import json

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def request_and_scrape(url, filter_key, Command):
    """ Take in URL, grab the relevant log line,
        return dict for comparison """

    JSON_LOG_FILE = "/var/www/django/logs/app.log"
    # Generate log event via http requests
    Command.run("curl --user-agent testinfra http://localhost:8000" + url)
    # Pick out the last log line from django logs
    # This is obviously only reliable test on a test instance with no
    # other incoming traffic.
    grab_log = Command.check_output("grep {0} {1} | tail -n 1".format(
                                    filter_key,
                                    JSON_LOG_FILE
                                    ))
    # Process JSON
    raw_json = json.loads(grab_log)[filter_key]
    # The current json structure uses the time as the key
    # its a pretty dumb design.
    filtered_json = raw_json[raw_json.keys()[0]]

    return filtered_json


def test_json_log_exception(Command):
    """
    Ensure json logging is working for exception
    """

    url = "/page-doesnt-exist/"

    request = {
                "data": {},
                "meta": {
                    "http_host": "localhost:8000",
                    "http_user_agent": "testinfra",
                    "path_info": url,
                    "remote_addr": "127.0.0.1"
                },
                "method": "GET",
                "path": url,
                "scheme": "http",
                "user": "AnonymousUser"
               }

    error_line = request_and_scrape(url, 'ERROR', Command)
    assert 'exception' in error_line
    assert error_line['request'] == request


def test_json_log_200(Command):
    """
    Ensure json logging is working for requests
    """

    should_return = {"request":
                        {"data": {}, 
                             "meta": {"http_host": "localhost:8000",
                                      "http_user_agent": "testinfra",
                                      "path_info": "/",
                                      "remote_addr": "127.0.0.1"},
                             "method": "GET",
                             "path": "/",
                             "scheme": "http",
                             "user": "AnonymousUser"},
                        "response": {
                            "charset": "utf-8",
                            "headers": {
                                "Content-Type": "text/html; charset=utf-8"
                                },
                            "reason": "OK",
                            "status": 200}}

    assert request_and_scrape('/','INFO', Command) == should_return
