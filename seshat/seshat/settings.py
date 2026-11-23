"""
Django settings for the SESHAT project.

Environment specific values (secret key, debug, hosts, database) live in
seshat_settings.py, which reads them from environment variables or a
`.env` file placed next to manage.py.

https://docs.djangoproject.com/en/6.1/topics/settings/
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

from pathlib import Path

from . import seshat_settings as my_settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
MEDIA_DIR = BASE_DIR / 'media'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = my_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = my_settings.DEBUG

ALLOWED_HOSTS = my_settings.ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = my_settings.CSRF_TRUSTED_ORIGINS


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'crispy_bootstrap5',
    'x_django_app',
    'django_db_logger',
    'rest_framework',
    'seshat.apps.SeshatConfig',
    'account.apps.AccountConfig',
    'stock.apps.StockConfig',
    'customer.apps.CustomerConfig',
    'vendor.apps.VendorConfig',
    'purchase.apps.PurchaseConfig',
    'sale.apps.SaleConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'seshat.middleware.ErrorPagesMiddleware',
]

ROOT_URLCONF = 'seshat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR, ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'seshat.middleware.debug',
                'seshat.middleware.theme',
            ],
        },
    },
]

WSGI_APPLICATION = 'seshat.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = my_settings.DATABASES


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = my_settings.TIME_ZONE

USE_I18N = True

USE_TZ = True

# Language folder
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

LANGUAGES = [
    ('en', 'English'),
    ('ar', 'العربية'),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR, ]
STATIC_ROOT = BASE_DIR / 'staticroot'

# Media folder for database media
MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_DIR

# Custom user accounts
AUTH_USER_MODEL = 'account.User'
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = 'Index'
LOGOUT_REDIRECT_URL = LOGIN_URL

# Logging: server errors are stored in the database (django-db-logger)
# and shown to administrators under Administration -> Log Entries
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        },
        'django.request': {
            'handlers': ['db_log', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Django REST framework (used by the report APIs)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

X_FRAME_OPTIONS = 'DENY'

# HTTPS hardening (SESHAT_HTTPS, on by default when debug is off)
SESSION_COOKIE_SECURE = my_settings.HTTPS
CSRF_COOKIE_SECURE = my_settings.HTTPS
SECURE_SSL_REDIRECT = my_settings.HTTPS
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30 if my_settings.HTTPS else 0
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Default primary key field type
# https://docs.djangoproject.com/en/6.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Backup, restore, import and export folders
DUMPDATA_FILENAME = 'SESHATdb'
VAR_DIR = my_settings.VAR_DIR
BACKUP_DIR = VAR_DIR / 'backups'
RESTORE_DIR = VAR_DIR / 'restores'
IMPORT_DIR = VAR_DIR / 'imports'
EXPORT_DIR = VAR_DIR / 'exports'

# Maximum upload size for restore / import files (10 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
