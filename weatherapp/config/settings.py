# File: config/settings.py

"""
Django settings for the WeatherWebApp project.

Loads secrets and configuration from a `.env` file in BASE_DIR. If
`.env` is missing or OPENWEATHER_API_KEY is unset, the app will
refuse to start, avoiding silent failures.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# ───────────────────────────────────────────────────────────────────────────────
# BASE_DIR & .env LOADING
# ───────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from BASE_DIR/.env (if it exists)
load_dotenv(BASE_DIR / '.env')

def get_env(var_name: str, default: str = None, required: bool = False) -> str:
    """
    Helper to fetch an environment variable and optionally enforce its presence.
    """
    val = os.getenv(var_name, default)
    if required and not val:
        raise ImproperlyConfigured(f"Required environment variable '{var_name}' not set.")
    return val

# ───────────────────────────────────────────────────────────────────────────────
# SECURITY & DEBUG
# ───────────────────────────────────────────────────────────────────────────────
SECRET_KEY = get_env('DJANGO_SECRET_KEY', default='unsafe-dev-secret-key', required=True)
DEBUG      = get_env('DJANGO_DEBUG', default='False') == 'True'

# ───────────────────────────────────────────────────────────────────────────────
# ALLOWED_HOSTS
# ───────────────────────────────────────────────────────────────────────────────
_raw = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in _raw.split(',') if h.strip()]

# ───────────────────────────────────────────────────────────────────────────────
# INSTALLED APPS & MIDDLEWARE
# ───────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'weather',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ───────────────────────────────────────────────────────────────────────────────
# TEMPLATES
# ───────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.user_preferences',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ───────────────────────────────────────────────────────────────────────────────
# DATABASES
# ───────────────────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ───────────────────────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ───────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Europe/Athens'
USE_I18N      = True
USE_TZ        = True

# ───────────────────────────────────────────────────────────────────────────────
# STATIC FILES
# ───────────────────────────────────────────────────────────────────────────────
STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ───────────────────────────────────────────────────────────────────────────────
# AUTH
# ───────────────────────────────────────────────────────────────────────────────
LOGIN_URL = '/login/'

# ───────────────────────────────────────────────────────────────────────────────
# OPENWEATHER API SETTINGS
# ───────────────────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY    = get_env('OPENWEATHER_API_KEY', required=True)
OPENWEATHER_BASE_URL   = get_env('OPENWEATHER_BASE_URL',
                                 default='https://api.openweathermap.org/data/2.5/forecast')

# ───────────────────────────────────────────────────────────────────────────────
# EMAIL (DEV)
# ───────────────────────────────────────────────────────────────────────────────
DEFAULT_FROM_EMAIL = 'xristos.andreopo@gmail.com'
EMAIL_BACKEND      = 'django.core.mail.backends.console.EmailBackend'

# ───────────────────────────────────────────────────────────────────────────────
# LOGGING
# ───────────────────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    },
}
