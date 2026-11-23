'''
Environment specific settings for SESHAT.

Every value can be overridden with an environment variable, or with a
KEY=VALUE line in a `.env` file placed next to manage.py. Nothing in this
file is secret: production values must come from the environment.
'''
from pathlib import Path
import os

# Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent


def _read_env_file():
    '''
    Read KEY=VALUE lines from BASE_DIR/.env
    '''
    values = {}
    env_file = BASE_DIR / '.env'
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip()
                if len(value) > 1 and value[0] == value[-1] and value[0] in '\'"':
                    value = value[1:-1]
                values[key.strip()] = value
    return values


# Priority: real environment > BASE_DIR/.env > defaults
_env_file_values = _read_env_file()


def env(name, default=None):
    '''
    Get a setting from the environment, falling back to BASE_DIR/.env
    '''
    return os.environ.get(name) or _env_file_values.get(name) or default


def env_bool(name, default=False):
    '''
    Read a boolean setting ("true", "1", "yes", "on" are True)
    '''
    value = env(name)
    if value is None:
        return default
    return str(value).strip().lower() in ('true', '1', 'yes', 'on')


def env_list(name, default=None):
    '''
    Comma separated list, e.g. "a.com, b.com" -> ['a.com', 'b.com']
    '''
    value = env(name)
    if value is None:
        return list(default or [])
    items = (item.strip().strip('\'"').strip() for item in value.split(','))
    return [item for item in items if item]


# Django debug mode (on for local development unless told otherwise)
DEBUG = env_bool('SESHAT_DEBUG', True)

# Django secret key: a development key is used only while DEBUG is on
SECRET_KEY = env('SESHAT_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-seshat-development-key-change-me'
    else:
        raise RuntimeError(
            'SESHAT_SECRET_KEY must be set when SESHAT_DEBUG is off')

# Django allowed hosts
ALLOWED_HOSTS = env_list(
                    'SESHAT_ALLOWED_HOSTS',
                    ['*'] if DEBUG else ['localhost', '127.0.0.1'])

# Trusted origins for CSRF (needed behind HTTPS proxies)
CSRF_TRUSTED_ORIGINS = env_list('SESHAT_CSRF_TRUSTED_ORIGINS')

# Time zone
TIME_ZONE = env('SESHAT_TIME_ZONE', 'Africa/Cairo')

# SESHAT database (SQLite by default)
DATABASES = {
    'default': {
        'ENGINE': env('SESHAT_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': env('SESHAT_DB_NAME', str(BASE_DIR / 'seshatdb.sqlite3')),
        'USER': env('SESHAT_DB_USER', ''),
        'PASSWORD': env('SESHAT_DB_PASSWORD', ''),
        'HOST': env('SESHAT_DB_HOST', ''),
        'PORT': env('SESHAT_DB_PORT', ''),
    }
}

# Runtime data folder (backups, restores, imports and exports)
VAR_DIR = Path(env('SESHAT_VAR_DIR', str(BASE_DIR / 'var')))

# Serve over HTTPS only: secure cookies, HTTPS redirect and HSTS
# (on by default in production, off while developing)
HTTPS = env_bool('SESHAT_HTTPS', not DEBUG)
