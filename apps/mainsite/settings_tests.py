# encoding: utf-8


from cryptography.fernet import Fernet

from .settings import *

# disable logging for tests
LOGGING = {}

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

CELERY_ALWAYS_EAGER = True
SECRET_KEY = 'aninsecurekeyusedfortesting'
UNSUBSCRIBE_SECRET_KEY = str(SECRET_KEY)
AUTHCODE_SECRET_KEY = Fernet.generate_key()
