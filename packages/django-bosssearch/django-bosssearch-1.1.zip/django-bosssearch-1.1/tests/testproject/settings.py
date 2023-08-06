from os.path import dirname, join
from django.conf import global_settings
from testproject.boss_keys import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = join(dirname(__file__), 'db', 'djangobosssearch.db')

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.sqlite3',
        "NAME": join(dirname(__file__), 'db', 'djangobosssearch.db')
    }
}

INSTALLED_APPS = (
    'testproject',
    'djangobosssearch',
    'django.contrib.humanize',
    'pagination',
)

MIDDLEWARE_CLASSES = global_settings.MIDDLEWARE_CLASSES + (
    'pagination.middleware.PaginationMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

ROOT_URLCONF = 'testproject.urls'

BOSS_SITE_SEARCH_DOMAIN = 'lipsum.com'
