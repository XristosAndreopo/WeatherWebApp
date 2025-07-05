# File: config/settings.py

"""
Django settings for the WeatherWebApp project.

This file centralizes all configuration, loading sensitive values from
environment variables (via a `.env` file) to keep secrets out of source control.
It is organized into logical sections, each clearly documented.

Sections:
  1. Base directory & environment loading
  2. Security & debug settings
  3. Hosts & CORS
  4. Installed apps & middleware
  5. URL configuration & WSGI
  6. Templates & context processors
  7. Database configuration
  8. Internationalization
  9. Static & media files
  10. Authentication
  11. Third‑party API settings
  12. Email backend
  13. Security hardening
  14. Logging
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# ───────────────────────────────────────────────────────────────────────────────
# 1. BASE DIR & .env LOADING
# ───────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')  # loads variables from .env into os.environ

def get_env(var_name: str, default: str = None, required: bool = False) -> str:
    """
    Retrieve an environment variable or return default.
    If required is True and the variable is missing/empty, raises.
    """
    val = os.getenv(var_name, default)
    if required and not val:
        raise ImproperlyConfigured(f"Missing required env var: {var_name}")
    return val

# ───────────────────────────────────────────────────────────────────────────────
# 2. SECURITY & DEBUG
# ───────────────────────────────────────────────────────────────────────────────

# Must set DJANGO_SECRET_KEY in .env for production
SECRET_KEY = get_env('DJANGO_SECRET_KEY', default='unsafe-dev-secret-key', required=True)

# Turn off debug in production by setting DJANGO_DEBUG=False
DEBUG = get_env('DJANGO_DEBUG', default='False') == 'True'

# ───────────────────────────────────────────────────────────────────────────────
# 3. HOSTS & CORS
# ───────────────────────────────────────────────────────────────────────────────

# Comma‑separated list in DJANGO_ALLOWED_HOSTS
_allowed = get_env('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]

# ───────────────────────────────────────────────────────────────────────────────
# 4. INSTALLED APPS & MIDDLEWARE
# ───────────────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
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

# ───────────────────────────────────────────────────────────────────────────────
# 5. URL CONFIGURATION & WSGI
# ───────────────────────────────────────────────────────────────────────────────

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ───────────────────────────────────────────────────────────────────────────────
# 6. TEMPLATES & CONTEXT PROCESSORS
# ───────────────────────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # global templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Default
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Project-specific
                'config.context_processors.user_preferences',
            ],
        },
    },
]

# ───────────────────────────────────────────────────────────────────────────────
# 7. DATABASE CONFIGURATION
# ───────────────────────────────────────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # for development; switch to Postgres in prod
    }
}

# ───────────────────────────────────────────────────────────────────────────────
# 8. INTERNATIONALIZATION
# ───────────────────────────────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Europe/Athens'
USE_I18N      = True
USE_TZ        = True

# ───────────────────────────────────────────────────────────────────────────────
# 9. STATIC & MEDIA FILES
# ───────────────────────────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # for collectstatic in production

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'         # if you support user uploads

# ───────────────────────────────────────────────────────────────────────────────
# 10. AUTHENTICATION
# ───────────────────────────────────────────────────────────────────────────────

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ───────────────────────────────────────────────────────────────────────────────
# 11. THIRD‑PARTY API SETTINGS
# ───────────────────────────────────────────────────────────────────────────────

OPENWEATHER_API_KEY  = get_env('OPENWEATHER_API_KEY', required=True)
OPENWEATHER_BASE_URL = get_env(
    'OPENWEATHER_BASE_URL',
    default='https://api.openweathermap.org/data/2.5/forecast'
)

# ───────────────────────────────────────────────────────────────────────────────
# 12. EMAIL BACKEND (DEVELOPMENT)
# ───────────────────────────────────────────────────────────────────────────────

DEFAULT_FROM_EMAIL = 'no-reply@weatherapp.local'
EMAIL_BACKEND      = 'django.core.mail.backends.console.EmailBackend'

# ───────────────────────────────────────────────────────────────────────────────
# 13. SECURITY HARDENING (PRODUCTION)
# ───────────────────────────────────────────────────────────────────────────────

if not DEBUG:
    # Use secure cookies
    SESSION_COOKIE_SECURE   = True
    CSRF_COOKIE_SECURE      = True
    # Prevent the browser from guessing content types
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # XSS filter
    SECURE_BROWSER_XSS_FILTER   = True
    # Clickjacking protection
    X_FRAME_OPTIONS             = 'DENY'
    # HTTPS redirect
    SECURE_SSL_REDIRECT         = True
    # HSTS
    SECURE_HSTS_SECONDS         = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD            = True

# ───────────────────────────────────────────────────────────────────────────────
# 14. LOGGING
# ───────────────────────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': get_env('DJANGO_LOG_LEVEL', default='INFO'),
    },
}

# ───────────────────────────────────────────────────────────────────────────────
# DEFAULT PRIMARY KEY FIELD
# ───────────────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
