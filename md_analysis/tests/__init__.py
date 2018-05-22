import os

import django


def configure_test_env():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_to_do.settings_dev")
    django.setup()

configure_test_env()