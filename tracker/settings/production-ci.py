from .production import *  # noqa: F403, F401

TEST_RUNNER = 'common.test_runner.SeededXMLRunner'
TEST_OUTPUT_DIR = "./test-results"
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_VERBOSE = 2

# Ignore errors for using Google test keys in production
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
