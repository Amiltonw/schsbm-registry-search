import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the .env file
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nrn_search.settings')

import numpy
application = get_wsgi_application()