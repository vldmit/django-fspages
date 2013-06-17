from django.conf.global_settings import *
from os.path import join as pjoin, abspath, dirname



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': pjoin(dirname(__file__), 'tests.sqlite'), # Or path to database file if using sqlite3.
    }
}

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)
TEMPLATE_DIRS = (
    pjoin(abspath(dirname(__file__)), 'templates'),
)
TEMPLATE_LOADERS = (
    'fspages.template.loaders.filesystem.I18NLoader',
    'django.template.loaders.app_directories.Loader'
)
ROOT_URLCONF = 'urls'
INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'fspages',
)
ALLOWED_HOSTS=['*']
