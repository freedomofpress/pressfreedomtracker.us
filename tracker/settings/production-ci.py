from .production import *


TEST_RUNNER = "common.test_runner.SeededXMLRunner"
TEST_OUTPUT_DIR = "/home/gcorn"
TEST_OUTPUT_FILE_NAME = "app-tests.xml"
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_VERBOSE = 2

# Ignore errors for using Google test keys in production
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]
