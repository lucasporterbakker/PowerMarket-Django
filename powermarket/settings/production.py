import os
import raven


<<<<<<< HEAD
DEBUG = True

ALLOWED_HOSTS = [
    '.powermarket.net',
    '.powermarket.uk',
    '.ec2-34-248-217-25.eu-west-1.compute.amazonaws.com',
    '.ec2-34-250-126-54.eu-west-1.compute.amazonaws.com',
]

MANAGERS = (
    ('PowerMarket', 'contact@powermarket.net'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ebdb',
        'USER': 'tekramrewop',
        'PASSWORD': 'TekramRewop',
        'HOST': 'localhost',
        'PORT': ''
    }
}

RAVEN_CONFIG = {
    'dsn': 'https://a742a62ddb604ab1bb198c6d498b184d:2ec77e8c09bc49aabfcbbce6bc47f2af@sentry.io/128989',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
