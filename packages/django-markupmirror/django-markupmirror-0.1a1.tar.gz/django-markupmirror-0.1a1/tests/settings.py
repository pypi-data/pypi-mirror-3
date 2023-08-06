"""Test settigs for django-markupmirror."""

import os


TESTS_PATH = os.path.abspath(os.path.dirname(__file__))


def tests_path_to(*parts):
    """Returns absolute path for ``parts`` relative to ``TESTS_PATH``."""
    return os.path.abspath(os.path.join(TESTS_PATH, *parts))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS = (
    'django_nose',
    'markupmirror',
    'markupmirror.feincms',
    'tests',
)

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'markupmirror.db',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'markupmirror-tests',
        'KEY_PREFIX': 'markupmirror-tests',
        'TIMEOUT': 300,
    }
}

MEDIA_ROOT = tests_path_to('media')
MEDIA_URL = '/media/'
STATIC_ROOT = tests_path_to('static')
STATIC_URL = '/media/'

USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'simple': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['simple'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# ### django-markupmirror

MARKUPMIRROR_DEFAULT_MARKUP_TYPE = 'markdown'


# ### django-nose

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--detailed-errors',
    '--verbose',
    '--with-coverage',
    '--cover-html',
    '--cover-html-dir=' + tests_path_to(os.path.pardir, 'docs', '_coverage'),
    '--cover-package=markupmirror',
]
