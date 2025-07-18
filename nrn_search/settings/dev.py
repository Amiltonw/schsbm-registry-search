from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['schsbmnationalregister-bbegcabze6b3dnea.canadacentral-01.azurewebsites.net']
STATIC_ROOT = BASE_DIR / 'staticfiles'
#why
# Database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Optional: Add development-specific apps
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# Optional: Add development-specific middleware
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# INTERNAL_IPS = [
#     '127.0.0.1',
# ]