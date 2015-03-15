import tempfile
import shutil
import os
import subprocess
import collections
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def get_files(npm_executable_path=None, npm_prefix_path=None):
    command = ['npm' or npm_executable_path, 'install']
    if npm_prefix_path:
        command.append('--prefix=' + npm_prefix_path)
    proc = subprocess.Popen(
        command,
        env={'PATH': os.environ.get('PATH')},
    )
    proc.wait()
    return os.path.join(npm_prefix_path, 'node_modules')


class NpmFinder(FileSystemFinder):
    def __init__(self, apps=None, *args, **kwargs):
        files = get_files(
            getattr(settings, 'NPM_EXECUTABLE_PATH', None),
            getattr(settings, 'NPM_PREFIX_PATH', None),
        )
        destination = getattr(settings, 'NPM_DESTINATION_PREFIX', '')
        self.locations = [
            (destination, files),
        ]
        self.storages = collections.OrderedDict()

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages[self.locations[0][1]] = filesystem_storage
