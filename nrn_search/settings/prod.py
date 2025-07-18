# INTENTIONAL SYNTAX ERROR TO TEST FILE LOADING
THIS_IS_A_DELIBERATE_ERROR

from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database for production
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

SECRET_KEY = os.environ.get('SECRET')

# Azure Storage settings for static and media files
INSTALLED_APPS += ['storages']

conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': conn_str_params['dbname'],
        'HOST': conn_str_params['host'],
        'USER': conn_str_params['user'],
        'PASSWORD': conn_str_params['password'],
    }
}
STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

STATIC_URL = f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{STATICFILES_LOCATION}/'
MEDIA_URL = f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{MEDIAFILES_LOCATION}/'

DEFAULT_FILE_STORAGE = 'nrn_search.custom_azure.AzureMediaStorage'
STATICFILES_STORAGE = 'nrn_search.custom_azure.AzureStaticStorage'

# Security settings (adjust as needed for your production environment)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'