"""
Django settings for my_to_do project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

from my_to_do.settings_prod import *

INSTALLED_APPS = [
    'cr_review_sys',
    'md_analysis'
]

# MIGRATION_MODULES = dict(
#     [(app, 'cr_review_sys.tests.migrations') for app in INSTALLED_APPS])

# create only once
MIGRATION_MODULES = {
    'cr_review_sys': "cr_review_sys.tests.migrations"
}

# we use this to workaround useless DBA
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testing_database.db'
    }
}
