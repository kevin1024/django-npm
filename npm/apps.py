import os

from django.apps import AppConfig
from django.conf import settings


class NPMConfig(AppConfig):
    name = 'npm'
    verbose_name = "NPM package installer"

    # app settings
    NPM_EXECUTABLE_PATH = getattr(settings, 'NPM_EXECUTABLE_PATH', 'npm')
    NPM_ROOT_PATH = getattr(settings, 'NPM_ROOT_PATH', os.getcwd())