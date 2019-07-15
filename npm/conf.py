import os
from django.conf import settings
from appconf import AppConf


class MyAppConf(AppConf):
    # app settings

    # Windows settings
    # node_executable = "D:\\Program Files\\nodejs\\node.exe"
    # npm_cli = os.path.join(os.path.dirname(node_executable),
    #                       "node_modules\\npm\\bin\\npm-cli.js")
    # NPM_EXECUTABLE_PATH = '"%s" "%s"' % (node_executable, npm_cli)
    EXECUTABLE_PATH = 'npm'
    ROOT_PATH = os.getcwd()

    STATIC_FILES_PREFIX = ''
    FINDER_USE_CACHE = True
    FILE_PATTERNS = None

    class Meta:
        prefix = 'npm'
