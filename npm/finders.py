import tempfile
import shutil
import os
import subprocess
from fnmatch import fnmatch
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.conf import settings

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

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

def matches_patterns(patterns, filename):
    if not patterns:
        return True
    for module, module_patterns in patterns.items():
        for module_pattern in module_patterns:
            if fnmatch(filename, os.path.join(module, module_pattern)):
                return True
    return False


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
        self.storages = OrderedDict()

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages[self.locations[0][1]] = filesystem_storage

    def find(self, path, all=False):
        patterns = getattr(settings, 'NPM_FILE_PATTERNS', None)
        if not matches_patterns(patterns, path):
            return []
        return super(NpmFinder, self).find(path, all=all)

    def list(self, ignore_patterns):
        """
        List all files in all locations.
        """
        patterns = getattr(settings, 'NPM_FILE_PATTERNS', None)
        results = super(NpmFinder, self).list(ignore_patterns)
        matches = [(path, storage) for path, storage in results if matches_patterns(patterns, path)]
        return matches
