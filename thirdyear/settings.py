"""Minimal settings module for Render deployment.

This file intentionally only defines the bare minimum settings required so
`django.setup()` can import installed apps in this repo during deployment.
"""
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Load secret key from environment for safety. Provide a fallback for local dev.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback')

DEBUG = os.environ.get('DEBUG', 'False') in ('True', 'true', '1')

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # Admin must be present for admin.site.urls
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party template helpers
    'widget_tweaks',
    # Local apps
    'accounts.apps.AccountsConfig',
    'asset_management.apps.AssetManagementConfig',
    'support_records.apps.SupportRecordsConfig',
    'thermal_rolls.apps.ThermalRollsConfig',
    'vendor_assistance.apps.VendorAssistanceConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Template settings: include the project-level `templates/` directory and enable
# app directories so templates like `templates/accounts/login.html` are found.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'thirdyear.urls'

WSGI_APPLICATION = 'thirdyear.wsgi.application'

# Minimal DB config using sqlite for default. On Render, DATABASE_URL env var can be used.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# If a DATABASE_URL environment variable is provided (e.g. on Render), use it
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # dj_database_url.parse returns a dict compatible with Django DATABASES setting
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL, conn_max_age=600)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Recommended default for modern Django projects
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# When behind a proxy (Render sets X-Forwarded-Proto), respect the header so
# Django knows the request is secure and can build HTTPS URLs correctly.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
