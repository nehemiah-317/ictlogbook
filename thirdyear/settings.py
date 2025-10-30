"""Minimal settings module for Render deployment.

This file intentionally only defines the bare minimum settings required so
`django.setup()` can import installed apps in this repo during deployment.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load secret key from environment for safety. Provide a fallback for local dev.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback')

DEBUG = os.environ.get('DEBUG', 'False') in ('True', 'true', '1')

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'thirdyear.urls'

WSGI_APPLICATION = 'thirdyear.wsgi.application'

# Minimal DB config using sqlite for default. On Render, DATABASE_URL env var can be used.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
