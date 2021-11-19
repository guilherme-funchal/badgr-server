from mainsite.settings import *


DATABASES = {
    'default': {},
    'badgr': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'badgr',
        'OPTIONS': {
           'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", 
           # "init_command": "SET storage_engine=InnoDB",  # Uncomment when using MySQL to ensure consistency across servers
        }
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'test_badgr_',
        'VERSION': 1,
    }
}


# django test speedups
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
DEBUG = False
logging.disable(logging.CRITICAL)

# EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'
