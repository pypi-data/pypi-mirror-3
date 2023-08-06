
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('My Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

import tempfile, os
from django import contrib
tempdata = tempfile.mkdtemp()
approot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
adminroot = os.path.join(contrib.__path__[0], 'admin')

DATABASES = {
    'default': {
        'NAME': os.path.join(tempdata, 'signalqueue-test.db'),
        'TEST_NAME': os.path.join(tempdata, 'signalqueue-test.db'),
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
    }
}

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = os.path.join(approot, 'static')
MEDIA_URL = '/face/'
STATIC_ROOT = os.path.join(adminroot, 'static', 'admin')[0]
STATIC_URL = '/staticfiles/'
ADMIN_MEDIA_PREFIX = '/admin-media/'
ROOT_URLCONF = 'settings.urlconf'

TEMPLATE_DIRS = (
    os.path.join(approot, 'templates'),
    os.path.join(adminroot, 'templates'),
    os.path.join(adminroot, 'templates', 'admin'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    #"django.core.context_processors.i18n", this is AMERICA
    "django.core.context_processors.media",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_nose',
    'delegate',
    'signalqueue',
)

import logging
LOGGING = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={ 'standard': { 'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s' }, },
    handlers={
        'default': { 'level':'DEBUG', 'class':'logging.StreamHandler', 'formatter':'standard', },
        'nil': { 'level':'DEBUG', 'class':'django.utils.log.NullHandler', },
    },
    loggers={
        'signalqueue': { 'handlers': ['default'], 'level': 'INFO', 'propagate': False },
    },
    root={ 'handlers': ['default'], 'level': 'INFO', 'propagate': False },
)

SQ_QUEUES = {
    'default': {                                                # you need at least one dict named 'default' in SQ_QUEUES
        'ENGINE': 'signalqueue.worker.backends.RedisSetQueue',  # required - full path to a QueueBase subclass
        'INTERVAL': 30, # 1/3 sec
        'OPTIONS': dict(port=8356),
    },
    'listqueue': {
        'ENGINE': 'signalqueue.worker.backends.RedisQueue',
        'INTERVAL': 30, # 1/3 sec
        'OPTIONS': dict(port=8356),
    },
    'db': {
        'ENGINE': 'signalqueue.worker.backends.DatabaseQueueProxy',
        'INTERVAL': 30, # 1/3 sec
        'OPTIONS': dict(app_label='signalqueue', modl_name='EnqueuedSignal'),
    },
}

SQ_ADDITIONAL_SIGNALS=['signalqueue.tests']
SQ_WORKER_PORT = 11201

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# package path-extension snippet.
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
