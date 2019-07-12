import os

from django.apps import AppConfig
from django.conf import settings


class NPMConfig(AppConfig):
    name = 'npm'
    verbose_name = "NPM package installer"

    # app settings

    # Windows settings
    # node_executable = "D:\\Program Files\\nodejs\\node.exe"
    # npm_cli = os.path.join(os.path.dirname(node_executable),
    #                       "node_modules\\npm\\bin\\npm-cli.js")
    # NPM_EXECUTABLE_PATH = '"%s" "%s"' % (node_executable, npm_cli)
    NPM_EXECUTABLE_PATH = getattr(settings, 'NPM_EXECUTABLE_PATH', 'npm')

    NPM_ROOT_PATH = getattr(settings, 'NPM_ROOT_PATH', os.getcwd())

    NPM_STATIC_FILES_PREFIX = getattr(settings, 'NPM_STATIC_FILES_PREFIX', '')
    NPM_FINDER_USE_CACHE = getattr(settings, 'NPM_FINDER_USE_CACHE', True)
    NPM_FILE_PATTERNS = getattr(settings, 'NPM_FILE_PATTERNS', None)
