from storages.backends.azure_storage import AzureStorage
from django.conf import settings

class AzureStaticStorage(AzureStorage):
    location = settings.STATICFILES_LOCATION
    file_overwrite = False

class AzureMediaStorage(AzureStorage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False