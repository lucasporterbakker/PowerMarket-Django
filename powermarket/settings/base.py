import os

from django.core.urlresolvers import reverse_lazy


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)

DEBUG = True

ALLOWED_HOSTS = []

PROJECT_NAME = 'PowerMarket'
PROJECT_VERSION = '0.3.0'

ADMINS = (
    ('Laurent Tupin', 'laurent.tupin@gmail.com'),
)
MANAGERS = (
    ('PowerMarket', 'contact@powermarket.net'),
)

SECRET_KEY = 'y(zhxp01x$y5ub&4#lof2xrzw1loi&1!&4^ozd_frtvpkoyj1n'

HTTP_PROTOCOL = 'https'
DOMAIN = 'www.powermarket.net'
SITE_URL = HTTP_PROTOCOL + '://' + DOMAIN
SITE_NAME = 'PowerMarket'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.gis',
    'django.contrib.humanize',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'analytical',
    'bootstrap3',
    'ckeditor',
    'ckeditor_uploader',
    'crispy_forms',
    'django_extensions',
    'django_inlinecss',
    'easy_thumbnails',
    'liststyle',
    'impersonate',
    'import_export',
    'private_storage',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'svg',
    'powermarket',
    'apps.landing',
    'apps.location',
    'apps.manager',
    'apps.nrel',
    'apps.solar',
    'apps.supplier',
    'apps.support',
    'apps.user',
    'django.contrib.admin',
    'django.contrib.sitemaps',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ROOT_URLCONF = 'powermarket.urls'
WSGI_APPLICATION = 'powermarket.wsgi.application'

SITE_ID = 1

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.request",
                "django.core.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django_settings_export.settings_export",
                "powermarket.context_processors.nice_greeting",
            ],
        },
    },
]

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_PASSWORD_MIN_LENGTH = 4
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_LOGOUT_ON_GET = True

LOGIN_REDIRECT_URL = reverse_lazy('manager:dashboard')

SOCIALACCOUNT_PROVIDERS = {
    'linkedin_oauth2': {
        'SCOPE': [
            'r_basicprofile',
            'r_emailaddress',
        ],
        'PROFILE_FIELDS': [
            'id',
            'first-name',
            'last-name',
            'email-address',
            'public-profile-url',
            'headline',
            'industry',
            'specialties',
            'positions',
        ],
    }
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

CKEDITOR_UPLOAD_PATH = "uploads/"

CONTACT_PHONE = ''
CONTACT_EMAIL = 'contact@powermarket.net'
SUPPORT_EMAIL = CONTACT_EMAIL

DEFAULT_FROM_EMAIL = 'Power Market <contact@powermarket.net>'
DEFAULT_ADMIN_EMAIL = 'Admin account <contact@powermarket.net>'

try:
    from .email import host, user, pw
    EMAIL_HOST = host
    EMAIL_HOST_USER = user
    EMAIL_HOST_PASSWORD = pw
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
except:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print("Could not retrieve email settings, using console output.")

MAPS_API_KEY = 'AIzaSyCiS7f7yHR4qZDm5ot2jwWbQQRteGA11k4'

NREL_API_KEY = 'skJHc63Rtu2C5jHt8nGtMx4xkVLGdpULbFqDwY11'
NREL_DEFAULT_DATASET = 'intl'
NREL_DEFAULT_MODULE_TYPE = 0
NREL_DEFAULT_SYSTEM_LOSSES = 14  # [%]
NREL_DEFAULT_ARRAY_TYPE = 1
NREL_DEFAULT_TILT = None
NREL_DEFAULT_AZIMUTH = None
NREL_DEFAULT_DC_AC_RATIO = None
NREL_DEFAULT_GCR = None
NREL_DEFAULT_INV_EFF = None  # [%]
NREL_DEFAULT_RADIUS = 1000  # [km]

REQUIRED_ELECTRICITY_BILLS = 12

DEFAULT_ADDRESS = 'Trafalgar Square, London WC2N 5DN, UK' #'3 West Way, Botley, Oxford OX2 0JB, UK'

PRIMARY_COLOR = '#248e57'
SECONDARY_COLOR = '#fea739'
THEME_COLOR = '#1a2238'

THUMBNAIL_ALIASES = {
    'solar.ExampleAssessment.image': {
        'medium': {'size': (400, 220), 'crop': True, 'quality': 99},
    }
}

PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR, 'private')
PRIVATE_STORAGE_AUTH_FUNCTION = 'apps.manager.functions.private_file_auth_function'

# Mappings.
SUPPORTED_COUNTRIES = {
    'United Kingdom': {
        'gmaps_reps': ['United Kingdom'],
    },
    'India': {
        'gmaps_reps': ['India'],
    },
}

SETTINGS_EXPORT = [
    'PROJECT_NAME',
    'PROJECT_VERSION',
    'ADMINS',
    'MANAGERS',
    'DEBUG',
    'PRIMARY_COLOR',
    'SECONDARY_COLOR',
    'THEME_COLOR',
    'CONTACT_PHONE',
    'CONTACT_EMAIL',
    'SUPPORT_EMAIL',
    'HTTP_PROTOCOL',
    'SITE_URL',
    'SITE_NAME',
    'MAPS_API_KEY',
    'NREL_API_KEY',
    'REQUIRED_ELECTRICITY_BILLS',
]

try:
    from .local import *
except ImportError:
    pass
