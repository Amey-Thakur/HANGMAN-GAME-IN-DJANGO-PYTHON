'''
***************************************************************************************************
* PROJ NAME: HANGMAN GAME IN DJANGO & PYTHON
* AUTHOR   : Amey Thakur ([GitHub](https://github.com/Amey-Thakur))
* CO-AUTHOR: Mega Satish ([GitHub](https://github.com/msatmod))
* REPO     : [GitHub Repository](https://github.com/Amey-Thakur/HANGMAN-GAME-IN-DJANGO-PYTHON)
* RELEASE  : September 2, 2022
* LICENSE  : MIT License (https://opensource.org/licenses/MIT)
* 
* DESCRIPTION:
* Global configuration and orchestration layer for the Hangman backend. This module 
* manages the computational environment, security protocols (middleware), static asset 
* synchronization, and session lifecycle parameters essential for stateful gameplay.
***************************************************************************************************
'''

import os
from pathlib import Path
from dotenv import load_dotenv

# Initialize environment variable orchestration
load_dotenv()

# Fundamental directory mapping: Base Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Protocol: Secret Key management (Externalized via environment)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-dev')

# Operational Mode: Debugging heuristics
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Network Policy: Hostname white-listing
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Module Aggregation: Application ecosystem mapping
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hangman.apps.HangmanConfig',
]

# Middleware Pipeline: Request/Response interceptors for security and sessions
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Integrated for performant static serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Global Route Mapping
ROOT_URLCONF = 'core.urls'

# Presentation Layer: Template engine configuration and context processors
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

# Gateway Interface Protocol
WSGI_APPLICATION = 'core.wsgi.application'

# Persistence Layer: SQLite engine chosen for portable academic archiving
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Auto-incrementing primary key standard
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Identity Verification: Authentication hardening (Standard Django Suite)
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

# Localization & Temporal Mapping
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Resource Coordination: Assets (CSS, JS, Media)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Asset Acceleration Strategy (Whitenoise)
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Session Dynamics: State persistence for uninterrupted gameplay
SESSION_COOKIE_AGE = 1200 # 20 Minute lifecycle
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

